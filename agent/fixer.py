import os
import time
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def fix_build_gradle(pom_xml: str, build_gradle: str, error_log: str) -> str:
    """
    Use OpenAI to fix a broken build.gradle file based on the pom.xml and error logs.

    Args:
        pom_xml (str): Contents of the pom.xml file.
        build_gradle (str): Current contents of the build.gradle file.
        error_log (str): Output of the failed gradle build.

    Returns:
        str: Updated build.gradle content (or original if retries fail).
    """
    prompt = f"""
You are a Gradle and Java build expert.
Given the following Maven pom.xml:

<pom.xml>
{pom_xml}
</pom.xml>

And the current build.gradle:

<build.gradle>
{build_gradle}
</build.gradle>

The following Gradle build error occurred:

<error>
{error_log}
</error>

Please return the corrected build.gradle content to resolve the issue.
Only return the fixed build.gradle file content. No explanations or markdown formatting.
"""

    for attempt in range(3):
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Gradle and Maven build assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
            )
            content = response.choices[0].message.content.strip()
            print(f"✅ Gradle fix received (attempt {attempt + 1})")
            return content
        except Exception as e:
            print(f"⚠️ OpenAI API attempt {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s

    print("❌ All attempts to fix build.gradle failed. Using original content.")
    return build_gradle