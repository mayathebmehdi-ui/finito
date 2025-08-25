#!/usr/bin/env python3
"""
Firecrawl Fallback Module
Dernier recours pour rechercher des informations manquantes spécifiques
"""

import os
import logging
from typing import Dict, Optional, List
from firecrawl import Firecrawl
import openai
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

logger = logging.getLogger(__name__)

class FirecrawlFallback:
    def __init__(self):
        # Initialisation de Firecrawl avec la clé API
        self.firecrawl_api_key = "fc-c8abcd00ce2c462daba5b66aed5b20d1"
        self.firecrawl = Firecrawl(api_key=self.firecrawl_api_key)
        
        # Configuration OpenAI avec vérification
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("❌ OPENAI_API_KEY non trouvée dans les variables d'environnement")
        
        self.openai_client = openai.OpenAI(api_key=openai_key)
        logger.info("✅ Firecrawl Fallback initialisé avec clés API valides")

    def is_information_missing(self, analysis_result: Dict) -> Dict[str, bool]:
        """
        Vérifie quelles informations sont manquantes dans l'analyse
        Retourne un dictionnaire indiquant ce qui doit être recherché
        """
        missing_info = {
            "shipping_policy": False,
            "return_policy": False, 
            "self_help_returns": False,
            "insurance": False
        }
        
        # Vérifier chaque champ pour détecter les informations manquantes
        for field in missing_info.keys():
            value = analysis_result.get(field, "")
            
            # Indicateurs d'informations manquantes (mode agressif)
            missing_indicators = [
                "information not available",
                "no information",
                "not provided",
                "not mentioned",
                "no specific",
                "was not provided",
                "not found",
                "unable to find",
                "could not determine",
                "",
                None
            ]
            
            # Plus agressif : considérer comme manquant si trop court ou trop vague
            if (any(indicator in str(value).lower() for indicator in missing_indicators) or 
                len(str(value).strip()) < 50 or  # Trop court
                "no -" in str(value).lower() or  # Commence par "No -"
                "yes -" in str(value).lower() or  # Commence par "Yes -" (souvent vague)
                str(value).lower().count("specific") > 0 or  # Contient "specific" = vague
                str(value).lower().count("however") > 0 or   # Contient "however" = incertain
                str(value).lower().count("mentioned") > 0):  # Contient "mentioned" = vague
                missing_info[field] = True
                logger.info(f"🔍 FIRECRAWL: Missing/insufficient information detected for: {field} (value: '{str(value)[:100]}...')")
        
        missing_count = sum(missing_info.values())
        if missing_count > 0:
            logger.info(f"🔥 FIRECRAWL: Total {missing_count} informations manquantes détectées")
        else:
            logger.info("✅ FIRECRAWL: Aucune information manquante")
        
        return missing_info

    def should_use_firecrawl(self, missing_info: Dict[str, bool], domain: str) -> bool:
        """
        Demande à OpenAI si on devrait utiliser Firecrawl pour ce domaine
        """
        missing_count = sum(missing_info.values())
        
        if missing_count == 0:
            return False
            
        try:
            prompt = f"""
            Analyze this e-commerce website: {domain}
            
            Missing information: {[field for field, is_missing in missing_info.items() if is_missing]}
            
            Should we use Firecrawl search API as a last resort to find this missing information?
            
            Consider:
            - Is this a major retailer that likely HAS this information online?
            - Would a web search likely find official policy pages?
            - Is the missing information critical for e-commerce analysis?
            
            Respond with only: YES or NO
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0
            )
            
            decision = response.choices[0].message.content.strip().upper()
            should_use = decision == "YES"
            
            logger.info(f"🤖 FIRECRAWL: OpenAI decision for {domain}: {decision}")
            if should_use:
                logger.info(f"✅ FIRECRAWL: OpenAI a autorisé l'utilisation de Firecrawl pour {domain}")
            else:
                logger.info(f"❌ FIRECRAWL: OpenAI a refusé l'utilisation de Firecrawl pour {domain}")
            return should_use
            
        except Exception as e:
            logger.error(f"❌ FIRECRAWL: Error checking necessity: {e}")
            # En cas d'erreur, utiliser Firecrawl si plus de 2 infos manquent
            fallback_decision = missing_count >= 2
            logger.info(f"🆘 FIRECRAWL: Fallback decision (≥2 missing): {'YES' if fallback_decision else 'NO'}")
            return fallback_decision

    def search_missing_information(self, domain: str, missing_info: Dict[str, bool]) -> Dict[str, str]:
        """
        Utilise Firecrawl pour rechercher les informations manquantes
        """
        results = {}
        
        # Construire les requêtes de recherche spécifiques
        # Nettoyer le domaine pour optimiser la recherche Firecrawl
        clean_domain = domain.replace("www.", "") if domain.startswith("www.") else domain
        
        search_queries = {
            "shipping_policy": f"shipping policy {clean_domain}",
            "return_policy": f"return policy {clean_domain}", 
            "self_help_returns": f"self service returns {clean_domain}",
            "insurance": f"protection plan warranty {clean_domain}"
        }
        
        for field, is_missing in missing_info.items():
            if not is_missing:
                continue
                
            try:
                logger.info(f"🔥 FIRECRAWL: Searching for {field} with query: {search_queries[field][:50]}...")
                
                # Recherche avec Firecrawl V2 API et scraping du contenu
                search_result = self.firecrawl.search(
                    query=search_queries[field],
                    limit=2  # Réduire à 2 pour avoir un contenu plus riche
                )
                logger.info(f"📡 FIRECRAWL: Search completed for {field}")
                
                if search_result and hasattr(search_result, 'web') and search_result.web:
                    # Scraper le contenu complet des URLs trouvées
                    content_pieces = []
                    
                    for result in search_result.web[:2]:  # Prendre les 2 premiers résultats web
                        if hasattr(result, 'url') and result.url:
                            try:
                                logger.info(f"📄 FIRECRAWL: Scraping content from {result.url[:60]}...")
                                
                                # Scraper le contenu complet de l'URL avec Firecrawl
                                scraped_content = self.firecrawl.scrape(
                                    url=result.url,
                                    formats=['markdown', 'html']
                                )
                                
                                if scraped_content and hasattr(scraped_content, 'markdown') and scraped_content.markdown:
                                    # Prendre le contenu markdown complet
                                    full_content = scraped_content.markdown
                                    logger.info(f"✅ FIRECRAWL: Scraped {len(full_content)} chars from {result.url[:30]}...")
                                    content_pieces.append(full_content[:3000])  # Limiter à 3000 chars pour OpenAI
                                elif scraped_content and hasattr(scraped_content, 'html') and scraped_content.html:
                                    # Fallback sur HTML si pas de markdown
                                    full_content = scraped_content.html
                                    logger.info(f"✅ FIRECRAWL: Scraped HTML {len(full_content)} chars from {result.url[:30]}...")
                                    content_pieces.append(full_content[:3000])
                                else:
                                    # Fallback sur titre + description
                                    fallback_content = f"Title: {result.title}\nDescription: {result.description}"
                                    content_pieces.append(fallback_content)
                                    logger.warning(f"🔄 FIRECRAWL: Using fallback content for {result.url[:30]}...")
                                    
                            except Exception as scrape_error:
                                logger.warning(f"⚠️ FIRECRAWL: Scraping failed for {result.url[:30]}: {scrape_error}")
                                # Fallback sur titre + description en cas d'erreur
                                fallback_content = f"Title: {result.title}\nDescription: {result.description}"
                                content_pieces.append(fallback_content)
                    
                    if content_pieces:
                        combined_content = "\n\n".join(content_pieces)
                        
                        # Analyser le contenu avec OpenAI
                        extracted_info = self._extract_specific_info(combined_content, field, domain)
                        
                        if extracted_info and extracted_info != "Information not available":
                            results[field] = extracted_info
                            logger.info(f"✅ FIRECRAWL: Successfully found {field}: {extracted_info[:100]}...")
                        else:
                            results[field] = "Information not available"
                            logger.warning(f"🔍 FIRECRAWL: No useful info extracted for {field}")
                    else:
                        results[field] = "Information not available"
                        logger.warning(f"📄 FIRECRAWL: No content found in search results for {field}")
                else:
                    results[field] = "Information not available"
                    logger.warning(f"🚫 FIRECRAWL: No web results found for {field}")
                    
            except Exception as e:
                logger.error(f"❌ FIRECRAWL: Search failed for {field}: {e}")
                results[field] = "Information not available"
        
        return results

    def _extract_specific_info(self, content: str, field: str, domain: str) -> str:
        """
        Utilise OpenAI pour extraire des informations spécifiques du contenu Firecrawl
        """
        try:
            field_prompts = {
                "shipping_policy": {
                    "task": "Extract shipping policy details",
                    "focus": "costs, delivery timeframes, shipping methods, free shipping thresholds, international shipping"
                },
                "return_policy": {
                    "task": "Extract return policy details", 
                    "focus": "return window, conditions, refund process, exchange options, return fees"
                },
                "self_help_returns": {
                    "task": "Extract self-service return information",
                    "focus": "online return initiation, return portals, customer account features, print labels"
                },
                "insurance": {
                    "task": "Extract protection plan/insurance information",
                    "focus": "coverage details, costs, how to purchase, what's covered, warranty options"
                }
            }
            
            field_info = field_prompts.get(field, {"task": field, "focus": "relevant details"})
            
            prompt = f"""
            You are analyzing content from {domain} to extract {field_info['task']}.
            
            Focus on: {field_info['focus']}
            
            Content to analyze:
            {content[:4000]}
            
            INSTRUCTIONS:
            1. Extract ONLY the specific information requested about {field_info['task']}
            2. Be comprehensive but concise
            3. Include specific details like prices, timeframes, conditions
            4. If no relevant information is found, respond with "Information not available"
            5. Format your response as clear, structured text (not JSON)
            
            Extract the {field_info['task']} information:
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,  # Augmenté pour des réponses plus complètes
                temperature=0
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"❌ Error extracting {field} info: {e}")
            return "Information not available"

    def enhance_analysis(self, analysis_result: Dict, domain: str) -> Dict:
        """
        Fonction principale pour améliorer l'analyse avec Firecrawl
        """
        try:
            logger.info(f"🚀 FIRECRAWL: Starting fallback analysis for {domain}")
            
            # 1. Vérifier quelles informations manquent
            missing_info = self.is_information_missing(analysis_result)
            
            if not any(missing_info.values()):
                logger.info("✅ FIRECRAWL: No missing information detected - skipping")
                return analysis_result
            
            # 2. Demander à OpenAI si on devrait utiliser Firecrawl
            if not self.should_use_firecrawl(missing_info, domain):
                logger.info("🚫 FIRECRAWL: OpenAI advised against using Firecrawl - skipping")
                return analysis_result
            
            # 3. Utiliser Firecrawl pour rechercher les informations manquantes
            logger.info("🔥 FIRECRAWL: Launching search for missing information")
            firecrawl_results = self.search_missing_information(domain, missing_info)
            
            # 4. Mettre à jour l'analyse avec les nouvelles informations
            enhanced_result = analysis_result.copy()
            enhancement_count = 0
            for field, new_info in firecrawl_results.items():
                if new_info != "Information not available":
                    enhanced_result[field] = new_info
                    enhanced_result[f"{field.replace('_policy', '_url').replace('self_help_returns', 'self_help_url').replace('insurance', 'insurance_url')}"] = f"https://{domain}/ (via Firecrawl search)"
                    enhancement_count += 1
                    logger.info(f"🎯 FIRECRAWL: Enhanced {field} with new information")
            
            logger.info(f"✅ FIRECRAWL: Process completed - {enhancement_count}/{len(firecrawl_results)} fields enhanced")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"❌ FIRECRAWL: Critical error during fallback process: {e}")
            logger.error(f"🔧 FIRECRAWL: Returning original analysis without enhancement")
            return analysis_result
