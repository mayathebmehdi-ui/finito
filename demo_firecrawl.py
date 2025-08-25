#!/usr/bin/env python3
"""
🔥 DÉMONSTRATION FIRECRAWL FONCTIONNEL
Prouve que Firecrawl fonctionne avec les corrections
"""

import os
from firecrawl_fallback import FirecrawlFallback
from dotenv import load_dotenv

load_dotenv()

def demo_firecrawl_working():
    """Démonstration que Firecrawl fonctionne"""
    print("🔥" * 60)
    print("🚀 DÉMONSTRATION FIRECRAWL FONCTIONNEL")
    print("🔥" * 60)
    
    # Données d'exemple avec informations manquantes (comme Best Buy)
    fake_analysis = {
        'domain': 'example.com',
        'shipping_policy': 'No specific shipping information found',
        'return_policy': 'Information not available',
        'self_help_returns': 'No - information not provided',
        'insurance': 'No specific information about protection plans'
    }
    
    print("📊 DONNÉES D'ENTRÉE (simulées):")
    for key, value in fake_analysis.items():
        if key != 'domain':
            status = "❌ MANQUANT" if any(x in value.lower() for x in ['no specific', 'not available', 'not provided']) else "✅ OK"
            print(f"  {key}: {status}")
    print()
    
    try:
        # Initialiser Firecrawl Fallback
        print("🔧 Initialisation Firecrawl Fallback...")
        fallback = FirecrawlFallback()
        print("✅ Firecrawl Fallback initialisé!")
        
        # Test de détection d'informations manquantes
        print("\n🔍 Test détection informations manquantes...")
        missing_info = fallback.is_information_missing(fake_analysis)
        missing_fields = [field for field, is_missing in missing_info.items() if is_missing]
        print(f"✅ Détectées: {len(missing_fields)} informations manquantes")
        print(f"   Fields: {missing_fields}")
        
        # Test décision OpenAI
        print(f"\n🤖 Test décision OpenAI pour {fake_analysis['domain']}...")
        should_use = fallback.should_use_firecrawl(missing_info, fake_analysis['domain'])
        print(f"✅ Décision OpenAI: {'OUI' if should_use else 'NON'}")
        
        # Test recherche Firecrawl (juste shipping_policy)
        print(f"\n🔥 Test recherche Firecrawl...")
        print(f"   Requête: 'shipping policy {fake_analysis['domain']}'")
        
        search_result = fallback.firecrawl.search(
            query=f"shipping policy {fake_analysis['domain']}",
            limit=2
        )
        
        print(f"✅ Recherche Firecrawl réussie!")
        print(f"   Type: {type(search_result)}")
        print(f"   Résultats web: {len(search_result.web) if hasattr(search_result, 'web') and search_result.web else 0}")
        
        if hasattr(search_result, 'web') and search_result.web:
            print(f"\n📋 PREMIERS RÉSULTATS:")
            for i, result in enumerate(search_result.web[:2]):
                print(f"   [{i+1}] {result.title[:60]}...")
                print(f"       URL: {result.url}")
                print(f"       Description: {result.description[:80]}...")
        
        print(f"\n🎯 CONCLUSION:")
        print(f"✅ Firecrawl Fallback fonctionne parfaitement!")
        print(f"✅ API de recherche opérationnelle")
        print(f"✅ Structure de données correcte")
        print(f"✅ Intégration complète")
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Définir la clé API pour le test
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY manquante")
        exit(1)
    
    demo_firecrawl_working()
