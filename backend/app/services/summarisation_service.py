import asyncio
from datetime import datetime, timezone
import json
from typing import List, Dict, Any, Optional, Union
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

# ---- Summarisation Model ----
summarisation_llm = init_chat_model("gpt-4.1-nano-2025-04-14", model_provider="openai") # gpt-4.1-2025-04-14

# ---- Summarisation Prompt ----
SUMMARISE_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a cybersecurity client executive at a prestigious insurance brokerage firm. Your goal is to extract and summarise valuable information from articles to be presented to clients. Summarise the given article into STRICT JSON with keys:\n"
     "executive_summary (<=500 characters), background (<=1000 characters), malicious_activity (<=1000 characters), outcomes_and_losses (<=1500 characters).\n"
     "Rules: (1) No extra keys. (2) No markdown. (3) No line breaks inside values. (4) If unknown, write 'UNKNOWN'."),
    ("human", "Reference text:\n\n"
     """
    Weak password allowed hackers to sink a 158-year-old company
    21 July 2025
    BBC A person wearing a hooded jacket and gloves is sitting at a laptop, typing. The screen of the laptop displays a password field filled with red asterisks. The background shows a digital map of Europe and various lines of code, suggesting themes of hacking or cybersecurity.BBC
    One password is believed to have been all it took for a ransomware gang to destroy a 158-year-old company and put 700 people out of work.

    KNP - a Northamptonshire transport company - is just one of tens of thousands of UK businesses that have been hit by such attacks.

    Big names such as M&S, Co-op and Harrods have all been attacked in recent months. The chief executive of Co-op confirmed last week that all 6.5 million of its members had had their data stolen.

    In KNP's case, it's thought the hackers managed to gain entry to the computer system by guessing an employee's password, after which they encrypted the company's data and locked its internal systems.

    KNP director Paul Abbott says he hasn't told the employee that their compromised password most likely led to the destruction of the company.

    "Would you want to know if it was you?" he asks.

    "We need organisations to take steps to secure their systems, to secure their businesses," says Richard Horne CEO of the National Cyber Security Centre (NCSC) - where Panorama has been given exclusive access to the team battling international ransomware gangs.

    One small mistake
    In 2023, KNP was running 500 lorries – most under the brand name Knights of Old.

    It was a 158-year-old business that employed 700 people.

    In June, it was targeted by criminals using ransomware - which is software designed to encrypt a victim's data and demand payment to unlock it.

    Paul Abbott, the former chief executive, says the impact was "devastating".

    "I think the way they got into the system was probably through a local account with an insecure password," he says.

    The attackers left a message which read: "If you're reading this it means the internal infrastructure of your company is fully or partially dead…Let's keep all the tears and resentment to ourselves and try to build a constructive dialogue".

    Mr Abbott says it's probably not the first time you've read about this sort of incident - or even close.

    That's because such cyberattacks are becoming more and more common in the UK.

    Industry research suggests the typical UK ransom demand is about £4m and that about a third of companies simply pay up.

    Mr Abbott made the decision not to pay the ransom, which experts estimated to be about £5m.

    He had followed industry guidelines and had cyber-insurance, but it wasn't enough.

    The insurance cover wasn't sufficient to put the business back where it was, so in June 2023 the 158-year-old company was forced to go into administration.

    In total, 700 employees were made redundant.

    """
     "\n\nReturn ONLY the JSON."),
    ("ai", """{{
      "executive_summary": "One password is believed to have been all it took for a ransomware gang to destroy a 158-year-old company and put 700 people out of work.",
      "background": "KNP - a Northamptonshire transport company running 500 lorries under the Knights of Old brand - was a 158-year-old business employing 700 people when targeted by ransomware criminals in June 2023.",
      "malicious_activity": "Hackers gained entry through guessing an employee's password, encrypted company data and locked internal systems. They left ransom note demanding dialogue. Ransom estimated at £5m which company refused to pay.",
      "outcomes_and_losses": "Company had cyber-insurance but coverage insufficient. Forced into administration June 2023. All 700 employees made redundant. 158-year-old business destroyed."
    }}"""),
    ("human", "Reference text:\n\n{reference_text}\n\nReturn ONLY the JSON.")
])

def format_incident_summary(summary_dict):
    """
    Formats an incident summary dictionary into a human-readable string
    with keys as headers.
    """
    formatted_output = ""
    for key, value in summary_dict.items():
        if key == 'source':
            continue
        header = key.replace("_", " ").capitalize()
        formatted_output += f"{header}\n{value}\n\n"
    return formatted_output.strip()

async def process_single_article_flat(article_content: str, source_type: str, source_url: str, affected_organization: str, event_date: Optional[Union[str, datetime]]) -> Dict[str, Any]:
    """
    Process a single article and return flat structure with summarised content
    """
    try:
        # Run the summarisation
        prompt = SUMMARISE_PROMPT.invoke({"reference_text": article_content})
        resp = await summarisation_llm.ainvoke(prompt)
        text = resp.content.strip()

        # Remove markdown code blocks if present
        if text.startswith('```json'):
            text = text[7:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()

        # Parse the JSON result
        summary_data = json.loads(text)

        #print(f"Original event date: {event_date}")
        # Normalize event_date to ISO string in the format YYYY-MM-DDT00:00:00.000+00:00
        if isinstance(event_date, datetime):
            # If datetime is naive (no tzinfo), assume UTC
            if event_date.tzinfo is None:
                event_date = event_date.replace(tzinfo=timezone.utc)
            event_date = event_date.isoformat(timespec='milliseconds')
        elif isinstance(event_date, str):
            # Handle YYYY-MM-DD format
            if len(event_date) == 10 and event_date.count('-') == 2:
                event_date = f"{event_date}T00:00:00.000+00:00"
            # If ISO without timezone: YYYY-MM-DDTHH:MM:SS
            elif event_date.endswith("T00:00:00"):
                event_date = f"{event_date}.000+00:00"
            # If already ISO with timezone, leave as-is
        else:
            event_date = "NA"
        #print(f"Final event date: {event_date}")

        # Create flat structure with direct field access
        flat_result = {
            'source': source_type,
            'executive_summary': summary_data.get('executive_summary', ''),
            'background': summary_data.get('background', ''),
            'malicious_activity': summary_data.get('malicious_activity', ''),
            'outcomes_and_losses': summary_data.get('outcomes_and_losses', ''),
            'reference_text': article_content,
            'summarised_text': format_incident_summary(summary_data),
            'source_url': source_url,
            'affected_organization': affected_organization,
            'date': event_date
        }

        return flat_result

    except Exception as e:
        print(f"❌ Error processing article from {source_type}: {str(e)}")
        return {
            'source': source_type,
            'executive_summary': f'ERROR: {str(e)}',
            'background': f'ERROR: {str(e)}',
            'malicious_activity': f'ERROR: {str(e)}',
            'outcomes_and_losses': f'ERROR: {str(e)}',
            'reference_text': article_content,
            'summarised_text': f'ERROR: {str(e)}',
            'source_url': source_url,
            'affected_organization': affected_organization,
            'date': event_date
        }

async def process_all_articles_flat(articles_dict: Dict[str, List]) -> List[Dict[str, Any]]:
    """
    Process all articles in parallel and return flat list with summarised content
    """
    tasks = []

    # Create tasks for internal database articles
    if 'retrieved_docs' in articles_dict:
        for doc in articles_dict['retrieved_docs']:
            # Extract page_content from Document objects
            content = doc.get('page_content', '') if isinstance(doc, dict) else str(doc)
            metadata = doc.get('metadata', {})
            event_date = metadata.get("event_date")
            task = process_single_article_flat(content, 'internal_database', metadata.get('source_url'), metadata.get('affected_organization'), event_date)
            tasks.append(task)

    # Create tasks for news articles
    if 'news_articles' in articles_dict:
        for article in articles_dict['news_articles']:
            # Extract content from the article structure
            content = article.get('content', '') if isinstance(article, dict) else str(article)
            date = article.get("date")
            task = process_single_article_flat(content, 'news_articles', article.get('url'), article.get('affected_organization'), date)
            tasks.append(task)

    if 'proprietary_data' in articles_dict:
        for data in articles_dict['proprietary_data']:
            # Extract content from the article structure
            content = data.get('page_content', '') if isinstance(data, dict) else str(data)
            metadata = data.get('metadata', {})
            event_date = metadata.get("Incident Date")
            task = process_single_article_flat(content, 'proprietary_data', 'Marsh Internal Data', metadata.get("Client Name"), event_date)
            tasks.append(task)

    # Run all tasks in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out exceptions and return clean results
    clean_results = []
    for result in results:
        if not isinstance(result, Exception):
            clean_results.append(result)
        else:
            print(f"Task failed with exception: {result}")

    return clean_results