#!/usr/bin/env python3
"""Test simple pour prouver que Firecrawl fonctionne"""

from firecrawl import Firecrawl

def test_firecrawl_works():
    print("🔥 TEST FIRECRAWL SIMPLE")
    print("=" * 40)
    
    try:
        # Test avec la clé API directe
        firecrawl = Firecrawl(api_key="fc-c8abcd00ce2c462daba5b66aed5b20d1")
        print("✅ Firecrawl initialisé")
        
        # Test de recherche simple
        result = firecrawl.search(
            query="amazon shipping policy",
            limit=1
        )
        
        print(f"✅ Recherche réussie!")
        print(f"   Type: {type(result)}")
        print(f"   A des résultats web: {hasattr(result, 'web') and bool(result.web)}")
        
        if hasattr(result, 'web') and result.web:
            first_result = result.web[0]
            print(f"   Premier résultat: {first_result.title[:50]}...")
            print(f"   URL: {first_result.url}")
            
        print("\n🎉 FIRECRAWL FONCTIONNE PARFAITEMENT!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    test_firecrawl_works()
