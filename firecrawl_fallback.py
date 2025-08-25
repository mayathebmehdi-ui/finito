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
        # Initialisation de Firecrawl avec la clé API depuis l'environnement
        firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
        if not firecrawl_key:
            raise ValueError("❌ FIRECRAWL_API_KEY non trouvée dans les variables d'environnement (.env)")
        self.firecrawl = Firecrawl(api_key=firecrawl_key)
        
        # Configuration OpenAI avec vérification
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("❌ OPENAI_API_KEY non trouvée dans les variables d'environnement")
        
        self.openai_client = openai.OpenAI(api_key=openai_key)
        
        # SEARCH-ONLY toggle: if true, do not scrape URLs; pass titles+descriptions to OpenAI
        self.search_only = str(os.getenv("FIRECRAWL_SEARCH_ONLY", "false")).strip().lower() in ("1", "true", "yes", "on")
        try:
            self.search_only_topk = int(os.getenv("FIRECRAWL_SEARCH_ONLY_TOPK", "5"))
        except Exception:
            self.search_only_topk = 5
        if self.search_only:
            logger.info(f"🛠️ FIRECRAWL: SEARCH_ONLY mode enabled (topK={self.search_only_topk})")
        logger.info("✅ Firecrawl Fallback initialisé avec clés API valides (OpenAI + Firecrawl)")

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

    def search_missing_information(self, domain: str, missing_info: Dict[str, bool]) -> Dict[str, Dict[str, Optional[str]]]:
        """
        Utilise Firecrawl pour rechercher les informations manquantes
        """
        results: Dict[str, Dict[str, Optional[str]]] = {}
        
        # Construire les requêtes de recherche spécifiques
        # Nettoyer le domaine pour optimiser la recherche Firecrawl
        clean_domain = domain.replace("www.", "") if domain.startswith("www.") else domain
        
        search_queries = {
            "shipping_policy": f"shipping policy {clean_domain}",
            "return_policy": f"return policy {clean_domain}", 
            "self_help_returns": f"self service returns {clean_domain}",
            "insurance": f"protection plan warranty {clean_domain}"
        }
        
        # Keywords to score the most relevant search item per field
        field_keywords = {
            "shipping_policy": ["shipping", "delivery", "ship", "shipping policy", "delivery options"],
            "return_policy": ["return", "refund", "exchange", "return policy", "returns"],
            "self_help_returns": [
                "start a return", "start an online return", "returns portal",
                "self-service", "guest help", "online return", "return label",
                "return barcode", "drive up returns", "self service"
            ],
            "insurance": ["protection plan", "warranty", "insurance", "allstate", "squaretrade"]
        }

        for field, is_missing in missing_info.items():
            if not is_missing:
                continue
                
            try:
                logger.info(f"🔥 FIRECRAWL: Searching for {field} with query: {search_queries[field][:50]}...")
                
                # Recherche avec Firecrawl (SEARCH UNIQUEMENT)
                try:
                    search_result = self.firecrawl.search(
                        query=search_queries[field],
                        limit=3,
                    )
                except TypeError:
                    # Compatibilité: anciennes versions Python SDK sans scrape_options
                    search_result = self.firecrawl.search(
                        query=search_queries[field],
                        limit=3
                    )
                logger.info(f"📡 FIRECRAWL: Search completed for {field}")

                # Normaliser les items (supporte .web, ['web'], ou liste directe)
                items = []
                if search_result:
                    if hasattr(search_result, 'web') and search_result.web:
                        items = search_result.web
                    elif isinstance(search_result, dict) and search_result.get('web'):
                        items = search_result['web']
                    elif isinstance(search_result, list):
                        items = search_result

                if items:
                    # SEARCH_ONLY: sort by relevance and aggregate topK titles/descriptions for OpenAI
                    if self.search_only:
                        def score_item_so(it) -> int:
                            getv = (lambda k: getattr(it, k) if hasattr(it, k) else (it.get(k) if isinstance(it, dict) else None))
                            title = str(getv('title') or '')
                            desc = str(getv('description') or '')
                            url = str(getv('url') or '')
                            hay = " ".join(filter(None, [title, desc, url])).lower()
                            score = sum(1 for kw in field_keywords.get(field, []) if kw in hay)
                            if field == "self_help_returns":
                                if "start an online return" in hay or "start a return" in hay:
                                    score += 2
                                if "help/article" in url or "returns" in url:
                                    score += 1
                            if field == "return_policy" and ("return policy" in hay or "returns & refunds" in hay):
                                score += 1
                            return score

                        sorted_items_so = sorted(items, key=score_item_so, reverse=True)
                        top_items: List[str] = []
                        for idx, it in enumerate(sorted_items_so[: self.search_only_topk], start=1):
                            getv = (lambda k: getattr(it, k) if hasattr(it, k) else (it.get(k) if isinstance(it, dict) else None))
                            url = getv('url')
                            title = getv('title')
                            desc = getv('description')
                            top_items.append("\n".join(filter(None, [
                                f"Candidate {idx}:",
                                f"Title: {title}" if title else None,
                                f"Description: {desc}" if desc else None,
                                f"URL: {url}" if url else None,
                            ])))
                        combined = "\n\n".join(top_items)
                        best_url = (getattr(sorted_items_so[0], 'url', None) if hasattr(sorted_items_so[0], 'url') else (sorted_items_so[0].get('url') if isinstance(sorted_items_so[0], dict) else None))
                        extracted_info = self._extract_specific_info(combined[:4000], field, domain)
                        results[field] = {"text": extracted_info or "Information not available", "url": best_url}
                        logger.info(f"✅ FIRECRAWL: SEARCH_ONLY extracted {field}")
                        continue

                    # Score and try multiple candidates to avoid picking a bad one (e.g., marketplace pages)
                    def score_item(it) -> int:
                        getv = (lambda k: getattr(it, k) if hasattr(it, k) else (it.get(k) if isinstance(it, dict) else None))
                        title = str(getv('title') or '')
                        desc = str(getv('description') or '')
                        url = str(getv('url') or '')
                        hay = " ".join(filter(None, [title, desc, url])).lower()
                        score = sum(1 for kw in field_keywords.get(field, []) if kw in hay)
                        # Heuristics: penalize marketplace/seller pages for consumer policies
                        if field in ("return_policy", "shipping_policy"):
                            if "marketplace" in hay or "seller" in hay:
                                score -= 2
                            if "help/article" in url or "cp/returns" in url or "return-policy" in url:
                                score += 2
                        return score

                    sorted_items = sorted(items, key=score_item, reverse=True)
                    success = False
                    chosen_url_for_logging = None

                    for idx, candidate in enumerate(sorted_items[:3], start=1):
                        getv = (lambda k: getattr(candidate, k) if hasattr(candidate, k) else (candidate.get(k) if isinstance(candidate, dict) else None))
                        url = getv('url')
                        markdown = getv('markdown')
                        title = getv('title')
                        desc = getv('description')
                        chosen_url_for_logging = url or chosen_url_for_logging
                        logger.info(f"🧪 FIRECRAWL: Trying candidate {idx} for {field}: {url}")

                        # Build content: prefer scraped markdown, fallback to title+description
                        if markdown:
                            combined_content = str(markdown)[:4000]
                        elif url:
                            try:
                                logger.info(f"🔄 FIRECRAWL: Scraping {url} for full content...")
                                scraped_content = self.firecrawl.scrape(
                                    url=url,
                                    formats=['markdown', 'html']
                                )
                                if scraped_content and hasattr(scraped_content, 'markdown') and scraped_content.markdown:
                                    combined_content = scraped_content.markdown[:4000]
                                    logger.info(f"✅ FIRECRAWL: Got {len(combined_content)} chars of markdown content")
                                elif scraped_content and hasattr(scraped_content, 'html') and scraped_content.html:
                                    combined_content = scraped_content.html[:4000]
                                    logger.info(f"✅ FIRECRAWL: Got {len(combined_content)} chars of HTML content")
                                else:
                                    parts = []
                                    if title:
                                        parts.append(f"Title: {title}")
                                    if desc:
                                        parts.append(f"Description: {desc}")
                                    combined_content = "\n".join(parts)[:1500] if parts else ""
                                    logger.warning(f"⚠️ FIRECRAWL: No markdown/html from scrape, using title+description")
                            except Exception as scrape_error:
                                logger.warning(f"❌ FIRECRAWL: Scrape failed for {url}: {scrape_error}")
                                parts = []
                                if title:
                                    parts.append(f"Title: {title}")
                                if desc:
                                    parts.append(f"Description: {desc}")
                                combined_content = "\n".join(parts)[:1500] if parts else ""
                        else:
                            parts = []
                            if title:
                                parts.append(f"Title: {title}")
                            if desc:
                                parts.append(f"Description: {desc}")
                            combined_content = "\n".join(parts)[:1500] if parts else ""

                        if combined_content:
                            extracted_info = self._extract_specific_info(combined_content, field, domain)
                            if extracted_info and extracted_info != "Information not available":
                                results[field] = {"text": extracted_info, "url": url}
                                logger.info(f"✅ FIRECRAWL: Extracted {field} from candidate {idx}")
                                success = True
                                break
                            else:
                                logger.warning(f"🔍 FIRECRAWL: Candidate {idx} yielded no useful info for {field}")

                    if not success:
                        results[field] = {"text": "Information not available", "url": chosen_url_for_logging}
                        logger.warning(f"🚫 FIRECRAWL: All candidates exhausted for {field}")
                else:
                    results[field] = {"text": "Information not available", "url": None}
                    logger.warning(f"🚫 FIRECRAWL: No search items found for {field}")
                    
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
            
            # 2. Decision gate: bypass if SEARCH_ONLY is forced
            if not self.search_only:
                if not self.should_use_firecrawl(missing_info, domain):
                    logger.info("🚫 FIRECRAWL: OpenAI advised against using Firecrawl - skipping")
                    return analysis_result
            else:
                logger.info("🔓 FIRECRAWL: SEARCH_ONLY mode - bypassing OpenAI decision gate")
            
            # 3. Utiliser Firecrawl pour rechercher les informations manquantes
            logger.info("🔥 FIRECRAWL: Launching search for missing information")
            firecrawl_results = self.search_missing_information(domain, missing_info)
            
            # 4. Mettre à jour l'analyse avec les nouvelles informations
            enhanced_result = analysis_result.copy()
            enhancement_count = 0
            for field, payload in firecrawl_results.items():
                new_text = payload.get("text") if isinstance(payload, dict) else None
                new_url = payload.get("url") if isinstance(payload, dict) else None
                if new_text and new_text != "Information not available":
                    enhanced_result[field] = new_text
                    # Map field to its URL field
                    url_field_map = {
                        "shipping_policy": "shipping_url",
                        "return_policy": "return_url",
                        "self_help_returns": "self_help_url",
                        "insurance": "insurance_url",
                    }
                    url_field = url_field_map.get(field)
                    if url_field and new_url:
                        enhanced_result[url_field] = new_url
                    enhancement_count += 1
                    logger.info(f"🎯 FIRECRAWL: Enhanced {field} with new information")
            
            logger.info(f"✅ FIRECRAWL: Process completed - {enhancement_count}/{len(firecrawl_results)} fields enhanced")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"❌ FIRECRAWL: Critical error during fallback process: {e}")
            logger.error(f"🔧 FIRECRAWL: Returning original analysis without enhancement")
            return analysis_result
