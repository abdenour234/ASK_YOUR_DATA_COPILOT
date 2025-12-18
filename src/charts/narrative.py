"""
Narrative Generator - Creates natural language insights from query results
Sprint 2 - Ticket 7: Enhanced with automatic RAG context retrieval
"""

import os
import sys
import json
import pandas as pd
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

load_dotenv()

class NarrativeGenerator:
    """Generates natural language insights from data results."""
    
    def __init__(self, use_openrouter: bool = True):
        """
        Initialize narrative generator.
        
        Args:
            use_openrouter: If True, uses OpenRouter API. If False, uses rule-based.
        """
        self.use_openrouter = use_openrouter
        # Try multiple free models as fallbacks (verified working models on OpenRouter)
        self.openrouter_models = [
            os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.2-3b-instruct:free"),
            "meta-llama/llama-3.1-8b-instruct:free",
            "google/gemini-flash-1.5:free",
            "nousresearch/hermes-3-llama-3.1-405b:free",
            "mistralai/mistral-7b-instruct:free"
        ]
        self.openrouter_model = self.openrouter_models[0]
        
    def generate(
        self, 
        df: pd.DataFrame, 
        user_query: str, 
        chart_type: Optional[str] = None
    ) -> str:
        """
        Generate narrative insights from data.
        
        Args:
            df: DataFrame with query results
            user_query: Original user question
            chart_type: Type of chart being displayed (bar, line, pie, etc.)
            
        Returns:
            String with natural language narrative
        """
        if df.empty:
            return "No data found for your query. Try adjusting your filters or criteria."
        
        try:
            if self.use_openrouter:
                return self._generate_with_llm(df, user_query, chart_type)
            else:
                return self._generate_with_rules(df, user_query, chart_type)
                
        except Exception as e:
            print(f"⚠️ Narrative generation failed: {e}")
            # Fallback to simple summary
            return self._generate_simple_summary(df, user_query)
    
    def _generate_with_llm(
        self, 
        df: pd.DataFrame, 
        user_query: str, 
        chart_type: Optional[str]
    ) -> str:
        """Generate narrative using LLM."""
        import requests
        
        # Prepare data summary
        data_summary = self._summarize_data(df, max_rows=10)
        
        # Build context section
        context_section = f"CHART TYPE: {chart_type}" if chart_type else ""
        
        # Build prompt
        prompt = f"""Tu es un data analyst qui raconte des histoires captivantes à partir de données pour des utilisateurs business.

QUESTION DE L'UTILISATEUR : "{user_query}"

RÉSULTATS DE LA REQUÊTE :
{data_summary}

{context_section}

TA MISSION : Crée un récit captivant et storytellé (2-4 phrases) qui :
1. **Raconte une histoire** avec les chiffres (début, développement, conclusion)
2. **Met en avant le résultat principal** avec des chiffres précis et leur signification
3. **Compare et contextualise** les données de manière narrative
4. **Termine par une perspective** ou une recommandation actionable

IMPORTANT :
- **Réponds UNIQUEMENT en français**
- Utilise des **chiffres précis** avec espaces pour les milliers (ex: 1 234 567)
- Adopte un **ton storytelling** : "Ce qui ressort...", "La tendance montre..."
- Écris en **texte brut uniquement** (pas de markdown, pas de bullet points)
- Reste **concis mais captivant**
- Si le type de graphique est mentionné, intègre-le naturellement dans le récit
- Si des termes portugais apparaissent, traduis-les naturellement (ex: "beleza_saude" → "Beauté & Santé")

EXEMPLE DE FORMAT :
"L'analyse révèle une domination claire de [catégorie] qui génère [montant précis], représentant [pourcentage]% du total. 
Cette performance s'explique par [insight], tandis que [deuxième catégorie] suit avec [montant]. 
Ces chiffres suggèrent qu'investir dans [recommandation] pourrait amplifier cette dynamique positive."

Maintenant, génère le récit en français :"""
        
        try:
            # Call OpenRouter API with fallback models
            api_key = os.getenv("OPENROUTER_API_KEY", "free")
            
            # Try each model in sequence until one works
            for model_idx, model in enumerate(self.openrouter_models):
                
                try:
                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost:8501"),
                            "X-Title": os.getenv("OPENROUTER_SITE_NAME", "Ask Your Data Copilot")
                        },
                        json={
                            "model": model,
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "Tu es un data analyst qui crée des récits captivants et perspicaces à partir de données, en utilisant des techniques de storytelling pour rendre les insights mémorables et engageants."
                                },
                                {
                                    "role": "user", 
                                    "content": prompt
                                }
                            ],
                            "temperature": 0.3,
                            "max_tokens": 500
                        },
                        timeout=20
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if 'choices' in result and len(result['choices']) > 0:
                            narrative = result['choices'][0]['message']['content'].strip()
                            # Clean up the response
                            narrative = narrative.replace('\n\n', '\n').replace('\n', ' ')
                            return narrative
                        else:
                            continue
                    elif response.status_code == 429:
                        continue
                    elif response.status_code == 404:
                        continue
                    else:
                        continue
                        
                except requests.exceptions.Timeout:
                    continue
                except requests.exceptions.RequestException as e:
                    continue
            
            # All models failed
            return self._generate_with_rules(df, user_query, chart_type)
                
        except Exception as e:
            return self._generate_with_rules(df, user_query, chart_type)
    
    def _generate_with_rules(
        self, 
        df: pd.DataFrame, 
        user_query: str,
        chart_type: Optional[str]
    ) -> str:
        """Generate narrative using rule-based logic."""
        # Identify main metric and dimension
        numeric_cols = df.select_dtypes(include=['number']).columns
        non_numeric_cols = df.select_dtypes(exclude=['number']).columns
        
        if len(numeric_cols) == 0 or len(df) == 0:
            return f"Found {len(df)} records matching your query."
        
        main_metric = numeric_cols[0] if len(numeric_cols) > 0 else None
        main_dimension = non_numeric_cols[0] if len(non_numeric_cols) > 0 else None
        
        # Get top values
        if main_metric and main_dimension:
            df_sorted = df.sort_values(main_metric, ascending=False)
            top_row = df_sorted.iloc[0]
            top_value = top_row[main_metric]
            top_label = str(top_row[main_dimension])
            
            total = df[main_metric].sum()
            percentage = (top_value / total * 100) if total > 0 else 0
            
            # Translate common Portuguese terms
            translated_label = self._translate_term(top_label)
            
            if len(df) > 1:
                second_row = df_sorted.iloc[1] if len(df) > 1 else None
                second_value = second_row[main_metric] if second_row is not None else 0
                second_label = str(second_row[main_dimension]) if second_row is not None else ""
                translated_second = self._translate_term(second_label)
                
                # Build narrative
                narrative = f"{translated_label} leads with {self._format_number(top_value)}"
                if total > 0:
                    narrative += f", representing {percentage:.1f}% of the total {self._format_number(total)}"
                
                if second_value > 0:
                    narrative += f". {translated_second} follows with {self._format_number(second_value)}"
                
                if chart_type:
                    narrative += f". As shown in the {chart_type} chart"
                
                narrative += "."
                return narrative
            else:
                return f"{translated_label} has {self._format_number(top_value)}."
        
        # Fallback simple summary
        return self._generate_simple_summary(df, user_query)
    
    def _summarize_data(self, df: pd.DataFrame, max_rows: int = 10) -> str:
        """Create text summary of DataFrame."""
        if df.empty:
            return "No data available."
        
        lines = []
        
        # Basic info
        lines.append(f"Results: {len(df):,} row(s), {len(df.columns)} column(s)")
        
        # Column types
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            lines.append(f"Numeric columns: {', '.join(numeric_cols)}")
        
        # Top results
        if len(df) > 0:
            lines.append(f"\nTop {min(len(df), max_rows)} results:")
            
            for idx, row in df.head(max_rows).iterrows():
                # Format the row nicely
                row_items = []
                for col in df.columns:
                    val = row[col]
                    if pd.isna(val):
                        continue
                    if isinstance(val, (int, float)):
                        if abs(val) >= 1000:
                            row_items.append(f"{col}: {self._format_number(val)}")
                        else:
                            row_items.append(f"{col}: {val:,.2f}")
                    else:
                        # Translate Portuguese terms in display
                        translated = self._translate_term(str(val))
                        row_items.append(f"{col}: {translated}")
                
                lines.append(f"  {idx+1}. " + "; ".join(row_items))
            
            if len(df) > max_rows:
                lines.append(f"  ... and {len(df) - max_rows} more")
        
        # Totals for numeric columns
        if numeric_cols:
            lines.append(f"\nTotals:")
            for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
                total = df[col].sum()
                lines.append(f"  {col}: {self._format_number(total)}")
        
        return "\n".join(lines)
    
    def _generate_simple_summary(self, df: pd.DataFrame, user_query: str) -> str:
        """Generate a simple fallback summary."""
        if df.empty:
            return "No data found for your query."
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) > 0:
            main_col = numeric_cols[0]
            total = df[main_col].sum()
            avg = df[main_col].mean() if len(df) > 0 else 0
            
            return f"Found {len(df):,} records. Total {main_col}: {self._format_number(total)} (average: {self._format_number(avg)})."
        else:
            return f"Found {len(df):,} records matching your query."
    
    def _translate_term(self, term: str) -> str:
        """Translate common Portuguese business terms to English."""
        translations = {
            # Product categories
            "beleza_saude": "Beauty & Health",
            "informatica": "Electronics",
            "moveis_decoracao": "Home Decor",
            "esporte_lazer": "Sports & Leisure",
            "relogios_presentes": "Watches & Gifts",
            "telefonia": "Telephony",
            "automotivo": "Automotive",
            "brinquedos": "Toys",
            "cool_stuff": "Cool Stuff",
            "ferramentas_jardim": "Garden Tools",
            "perfumaria": "Perfumery",
            "cama_mesa_banho": "Bed & Bath",
            "eletrodomesticos": "Home Appliances",
            "eletroportateis": "Portable Appliances",
            "fashion_calcados": "Fashion Footwear",
            "fashion_roupa_masculina": "Men's Fashion",
            "fashion_roupa_feminina": "Women's Fashion",
            "fashion_underwear_e_moda_praia": "Underwear & Swimwear",
            "fashion_esporte": "Sportswear",
            "fashion_bolsas_e_acessorios": "Bags & Accessories",
            
            # Regions/States
            "sao_paulo": "São Paulo",
            "rio_de_janeiro": "Rio de Janeiro",
            "minas_gerais": "Minas Gerais",
            "espirito_santo": "Espírito Santo",
            "parana": "Paraná",
            "santa_catarina": "Santa Catarina",
            "rio_grande_do_sul": "Rio Grande do Sul",
            "bahia": "Bahia",
            "pernambuco": "Pernambuco",
            "ceara": "Ceará",
            
            # Metrics
            "receita": "Revenue",
            "vendas": "Sales",
            "lucro": "Profit",
            "quantidade": "Quantity",
            "valor": "Value",
            "total": "Total",
            "media": "Average"
        }
        
        # Check for exact match first
        if term in translations:
            return translations[term]
        
        # Check for partial matches or lowercase
        term_lower = term.lower()
        for key, value in translations.items():
            if key in term_lower:
                return value
        
        # Return original with underscores replaced
        return term.replace('_', ' ').title()
    
    def _format_number(self, num: float) -> str:
        """Format number with commas and appropriate precision."""
        if pd.isna(num):
            return "N/A"
        
        abs_num = abs(num)
        
        if abs_num >= 1_000_000_000:
            return f"{num/1_000_000_000:,.1f}B"
        elif abs_num >= 1_000_000:
            return f"{num/1_000_000:,.1f}M"
        elif abs_num >= 1_000:
            return f"{num:,.0f}"
        elif abs_num >= 1:
            return f"{num:,.2f}"
        else:
            return f"{num:.3f}"


# Convenience function
def generate_narrative(
    df: pd.DataFrame,
    query: str,
    chart_type: Optional[str] = None,
    use_llm: bool = True
) -> str:
    """
    Convenience function to generate narrative.
    
    Args:
        df: DataFrame with results
        query: Original user question
        chart_type: Type of chart
        use_llm: Whether to use LLM
        
    Returns:
        Narrative string
    """
    generator = NarrativeGenerator(use_openrouter=use_llm)
    return generator.generate(df, query, chart_type)


# Test function
if __name__ == "__main__":
    
    # Create sample data
    sample_data = {
        'product_category': ['beleza_saude', 'informatica', 'moveis_decoracao', 'esporte_lazer', 'relogios_presentes'],
        'revenue': [1234567.89, 987654.32, 876543.21, 765432.10, 654321.09],
        'orders': [1234, 987, 876, 765, 654]
    }
    
    df = pd.DataFrame(sample_data)
    query = "What are the top selling product categories?"
    narrative_llm = generate_narrative(df, query, use_llm=True)
    print(narrative_llm)