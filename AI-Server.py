from quart import Quart, request, jsonify
import httpx
import json

app = Quart(__name__)

OPENAI_API_KEY = "lm-studio"
BASE_URL = "http://localhost:1234/v1"

@app.route('/chat', methods=['POST'])
async def get_chat_response():
    data = await request.get_json()
    history = data.get('history', [])

    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    json_data = {
        "model": "huggingfaceh4_zephyr-7b-beta",
        "messages": history,
        "temperature": 0.7,
        "stream": True,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/chat/completions", json=json_data, headers=headers)

        # Ensure the response is successful.
        if response.status_code == 200:
            # Initialize a variable to hold the concatenated content.
            full_content = ""
            # Decode the streamed response.
            for line in response.text.split("\n"):
                if line.startswith("data:"):
                    # Extract the JSON part of the line.
                    json_part = line[5:]
                    try:
                        data = json.loads(json_part)
                        # Extract the content from the response and concatenate.
                        content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        full_content += content
                    except json.JSONDecodeError:
                        print("Error decoding JSON from chunk")

            # At this point, `full_content` holds the aggregated response.
            print("Aggregated response from OpenAI:", full_content)
            # Add the final message to history.
            new_message = {"role": "assistant", "content": full_content}
            history.append(new_message)

            return jsonify({"history": history})
        else:
            return jsonify({"error": "Bad response from OpenAI API.", "status_code": response.status_code}), 500

if __name__ == "__main__":
    app.run(debug=True)
