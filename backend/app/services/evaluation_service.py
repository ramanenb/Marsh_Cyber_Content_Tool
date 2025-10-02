# ==================== EVALUATION TOOLS ====================
# Apply nest_asyncio patch for faster async eval submission in notebooks
import nest_asyncio
nest_asyncio.apply()

# Enhanced parallel processing with BOTH hallucination and summarisation checks
from phoenix.evals import (
    OpenAIModel,
    llm_classify,
)
from collections import OrderedDict
import pandas as pd
from typing import Any, Dict, List

# Set up the evaluation model
evaluation_model = OpenAIModel(
    model="gpt-5-nano-2025-08-07",
    temperature=1.0,
)

# Hallucination evaluation setup
HALLUCINATION_PROMPT_RAILS_MAP = OrderedDict({
    0: "Fully factual",
    1: "Largely factual",
    2: "hallucinated"
})

# Summarisation evaluation setup
SUMMARISER_PROMPT_RAILS_MAP = OrderedDict({
    0: "good",
    1: "average",
    2: "bad"
})

hallucination_rails = list(HALLUCINATION_PROMPT_RAILS_MAP.values())
summariser_rails = list(SUMMARISER_PROMPT_RAILS_MAP.values())

# Evaluation templates
SUMMARISATION_PROMPT_MARSH_WITH_EXPLANATION = """
You are comparing the summary text and it's original document and trying to determine if the summary is good. The summary will be split into 4 parts, executive_summary, background, malicious_activity, outcomes_and_losses.
Here is the data:
    [BEGIN DATA]
    ************
    [executive_summary]: {executive_summary}
    [background]: {background}
    [malicious_activity]: {malicious_activity}
    [outcomes_and_losses]: {outcomes_and_losses}
    ************
    [Original Document]: {input}
    [END DATA]
Compare the Summary of the four components (executive_summary, background, malicious_activity, outcomes_and_losses) above to the Original Document. DO note the character counts of executive_summary (in no more than 500 characters), background (in no more than 600 characters), malicious_activity (in no more than 600 characters), outcomes_and_losses (in no more than 700 characters) when evaluating the quality of the summary.

First, write out in a step by step manner an EXPLANATION to show how to determine if each of the executive_summary, background, malicious_activity, outcomes_and_losses is comprehensive, concise, coherent, and
independent relative to the Original Document. Avoid simply stating the correct answer at the
outset. Your response LABEL must be a single word, either "good", "average" or "bad", and should not contain
any text or characters aside from that. "bad" means that the Summary is not comprehensive, concise,
coherent, and independent relative to the Original Document. "good" means the Summary is
comprehensive, concise, coherent, and independent relative to the Original Document. "average" means the summary did not furfil most but not all of the 4 criteria of comprehensive, concise, coherent, and independent relative to the Original Document.

Example response:
************
EXPLANATION: An explanation of your reasoning for why the label is "good", "bad" or "average"
LABEL: "good", "bad" or "average"
************

EXPLANATION:"""

HALLUCINATION_PROMPT_TEMPLATE_MARSH_WITH_EXPLANATION = """
In this task, you will be presented with a query, a reference text and an answer. The answer is
generated to the question based on the reference text. The answer may contain false information. You
must use the reference text to determine if the answer to the question contains false information,
if the answer is a hallucination of facts. Your objective is to determine whether the answer text
contains factual information and is not a hallucination. A 'hallucination' refers to
an answer that is not based on the reference text or assumes information that is not available in
the reference text.

    [BEGIN DATA]
    ************
    [Query]: {input}
    ************
    [Reference text]: {reference}
    ************
    [Answer]: {output}
    ************
    [END DATA]

    Is the answer above factual or hallucinated based on the query and reference text?

Please read the query, reference text and answer carefully, then write out in a step by step manner
an EXPLANATION to show how to determine if the answer is "Fully factual", "Largely factual" or "hallucinated". Avoid simply
stating the correct answer at the outset. Your response LABEL should be a single word: either
"Fully factual", "Largely factual" or "hallucinated", and it should not include any other text or characters. "hallucinated"
indicates that the answer provides factually inaccurate information to the query based on the
reference text. "Largely factual" indicates that the answer to the question is correct relative to the
reference text, and does not contain made up information, but may contain some ungrounded claims. "Fully factual" indicates that the answer to the question is correct relative to the
reference text, and does not contain made up information.

Example response:
************
EXPLANATION: An explanation of your reasoning for why the label is "Fully factual", "Largely factual" or "hallucinated"
LABEL: "Fully factual", "Largely factual" or "hallucinated"
************

EXPLANATION:"""

async def process_articles_with_dual_evaluation(articles_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Add BOTH hallucination and summarisation classification to each processed article
    """

    user_prompt = "Based on the reference_text, which is information scrapped from a news article, Summarise to include the executive_summary (in no more than 500 characters), background (in no more than 600 characters), malicious_activity (in no more than 600 characters), outcomes_and_losses (in no more than 700 characters)."

    # ==================== HALLUCINATION EVALUATION ====================

    # Prepare data for hallucination evaluation
    hallucination_eval_data = []
    for article in articles_list:
        hallucination_eval_data.append({
            'input': user_prompt,
            'reference': article['reference_text'],
            'output': article['summarised_text']
        })

    # Create DataFrame for hallucination evaluation
    hallucination_df = pd.DataFrame(hallucination_eval_data)

    # Run hallucination classification
    hallucination_classifications = llm_classify(
        data=hallucination_df,
        template=HALLUCINATION_PROMPT_TEMPLATE_MARSH_WITH_EXPLANATION,
        model=evaluation_model,
        rails=hallucination_rails,
        provide_explanation=True,
    )

    # ==================== SUMMARISATION EVALUATION ====================

    # Prepare data for summarisation evaluation
    summarisation_eval_data = []
    for article in articles_list:
        summarisation_eval_data.append({
            'input': article['reference_text'],  # Original document
            'executive_summary': article['executive_summary'],
            'background': article['background'],
            'malicious_activity': article['malicious_activity'],
            'outcomes_and_losses': article['outcomes_and_losses']
        })

    # Create DataFrame for summarisation evaluation
    summarisation_df = pd.DataFrame(summarisation_eval_data)

    # Run summarisation quality classification
    summariser_classifications = llm_classify(
        data=summarisation_df,
        template=SUMMARISATION_PROMPT_MARSH_WITH_EXPLANATION,
        model=evaluation_model,
        rails=summariser_rails,
        provide_explanation=True,
    )

    # ==================== COMBINE RESULTS ====================

    enhanced_articles = []
    for i, article in enumerate(articles_list):
        enhanced_article = article.copy()  # Copy original article data

        # Add hallucination classification data
        enhanced_article['hallucination_classification'] = hallucination_classifications['label'].iloc[i]
        enhanced_article['hallucination_explanation'] = hallucination_classifications['explanation'].iloc[i]

        # Add summarisation classification data
        enhanced_article['summariser_classification'] = summariser_classifications['label'].iloc[i]
        enhanced_article['summariser_explanation'] = summariser_classifications['explanation'].iloc[i]

        enhanced_articles.append(enhanced_article)

    return enhanced_articles