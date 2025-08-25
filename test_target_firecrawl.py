#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firecrawl_fallback import FirecrawlFallback

# Simuler exactement le résultat Target.com problématique
target_result = {
    "domain": "target.com",
    "shipping_policy": "Shipping charges may be refunded depending on the reason for your refund.",
    "return_policy": "Exchanges are offered in store on most items based on the return policy window.",
    "self_help_returns": "No - returns require contacting Target Guest Services or visiting a store",
    "insurance": "No - no specific insurance or protection plans mentioned"
}

print("🎯 TEST: Simulation du résultat Target.com problématique")
print("=" * 60)

try:
    fallback = FirecrawlFallback()
    print("✅ Firecrawl Fallback initialisé")
    
    # Test de détection des informations manquantes
    missing = fallback.is_information_missing(target_result)
    print(f"\n🔍 Informations manquantes détectées: {missing}")
    
    for field, is_missing in missing.items():
        if is_missing:
            value = target_result.get(field, "")
            print(f"   ❌ {field}: '{value}'")
        else:
            print(f"   ✅ {field}: OK")
    
    # Test si Firecrawl sera utilisé
    should_use = fallback.should_use_firecrawl(target_result, "target.com")
    print(f"\n🔥 Firecrawl sera-t-il utilisé? {should_use}")
    
    if should_use:
        print("\n🚀 EXCELLENT! Firecrawl va maintenant enrichir les données Target.com!")
        print("   Les pages Allstate Protection Plans seront trouvées!")
    else:
        print("\n❌ PROBLÈME: Firecrawl ne sera pas utilisé")
        print("   Les informations d'assurance Target ne seront pas trouvées")

except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
