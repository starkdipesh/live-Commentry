import json
import os
from pathlib import Path

def prepare_for_unsloth(dataset_dir, output_file):
    """
    Converts local Gold Dataset logs into a format compatible with Unsloth Fine-Tuning.
    Target format: List of dictionaries with 'instruction', 'input', and 'output'.
    """
    dataset_path = Path(dataset_dir)
    prepared_data = []

    # Iterate through all log files
    log_files = sorted(dataset_path.glob("log_*.json"))
    
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract relevant fields
            user_input = data.get("user_input", "[Observation]")
            context = data.get("context", "")
            
            # Identify where the AI's response starts in the log
            # Usually format is "Visual: ... | Reply: ..."
            if "Reply:" in context:
                visual_facts, ai_reply = context.split("Reply:", 1)
                visual_facts = visual_facts.replace("Visual:", "").strip()
                ai_reply = ai_reply.strip()
            else:
                visual_facts = context
                ai_reply = "..." # Fallback

            # Create the training sample
            sample = {
                "instruction": "You are Parthasarathi, the world's best life-long all-rounder partner. Analyze the visual facts and user speech, then provide a witty Hinglish response.",
                "input": f"Visuals: {visual_facts}\nUser says: {user_input}",
                "output": ai_reply
            }
            prepared_data.append(sample)
            
        except Exception as e:
            print(f"Skipping {log_file} due to error: {e}")

    # Save the final training file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(prepared_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Prepared {len(prepared_data)} samples for the Cloud Forge.")
    print(f"📁 Training file saved to: {output_file}")

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DATASET_DIR = BASE_DIR / "training_data" / "gold_dataset"
    OUTPUT_FILE = BASE_DIR / "training_data" / "unsloth_training_data.json"
    
    prepare_for_unsloth(DATASET_DIR, OUTPUT_FILE)
