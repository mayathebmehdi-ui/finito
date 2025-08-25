#!/bin/bash

# Script pour tester le Firecrawl fallback sur différents sites

echo "🧪 SCRIPT DE TEST FIRECRAWL FALLBACK"
echo "===================================="

API_URL="http://localhost:8001"

# Fonction pour tester un site
test_site() {
    local url="$1"
    local name="$2"
    
    echo ""
    echo "🎯 Test: $name ($url)"
    echo "-----------------------------------"
    
    # Lancer l'analyse
    echo "📤 Envoi de la requête..."
    response=$(curl -s -X POST "$API_URL/analyze" \
        -H "Content-Type: application/json" \
        -d "{\"url\": \"$url\"}")
    
    # Extraire le job_id
    job_id=$(echo "$response" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$job_id" ]; then
        echo "✅ Job créé: $job_id"
        echo "⏳ Attente de l'analyse (regardez les logs API)..."
        
        # Attendre et vérifier le résultat
        sleep 15
        
        echo "📥 Récupération du résultat..."
        result=$(curl -s "$API_URL/job/$job_id")
        
        # Afficher le status
        status=$(echo "$result" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        echo "📊 Status: $status"
        
        if [ "$status" = "completed" ]; then
            echo "🎉 Analyse terminée ! Vérifiez les résultats avec:"
            echo "   curl -s $API_URL/results | jq '.[-1]'"
        fi
    else
        echo "❌ Erreur lors de la création du job"
        echo "Response: $response"
    fi
}

# Vérifier si l'API est démarrée
echo "🔍 Vérification de l'API..."
if ! curl -s "$API_URL/" >/dev/null 2>&1; then
    echo "❌ API non disponible sur $API_URL"
    echo "💡 Démarrez d'abord: ./start_with_firecrawl.sh"
    exit 1
fi

echo "✅ API disponible!"

# Tests sur différents sites
echo ""
echo "🎯 TESTS AUTOMATIQUES"
echo "====================="

# Test 1: Site avec informations manquantes probables
test_site "https://www.costco.com" "Costco"

# Test 2: Site e-commerce moyen
test_site "https://www.bestbuy.com" "Best Buy"

echo ""
echo "🏁 TESTS TERMINÉS"
echo "================"
echo "💡 Conseils:"
echo "   - Regardez les logs de l'API pour voir Firecrawl en action"
echo "   - Cherchez les messages: 🔍 🤖 🔥 ✅"
echo "   - Vérifiez les résultats: curl -s $API_URL/results | jq"
