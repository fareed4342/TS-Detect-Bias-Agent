from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import os
import uuid
from botocore.config import Config

app = Flask(__name__)
CORS(app)

aws_config = Config(
    region_name='ap-southeast-1',
    retries={
        'max_attempts': 3,
        'mode': 'standard'
    }
)

user_sessions = {}

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json

    # Get or create session ID
    session_id = data.get('session_id')
    if not session_id or session_id not in user_sessions:
        session_id = str(uuid.uuid4())
        user_sessions[session_id] = True

    try:
        client = boto3.client(
            'bedrock-agent-runtime',
            region_name='ap-southeast-1',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            config=aws_config
        )

        response = client.invoke_agent(
            agentId='Q5GWZKCXD6',
            agentAliasId='TSTALIASID',
            sessionId=session_id,
            inputText=data['message']
        )

        # ✅ Correct way to collect streamed content
        result = ""
        for event in response.get("completion", []):
            chunk = event.get("chunk")
            if chunk and "bytes" in chunk:
                result += chunk["bytes"].decode("utf-8")

        return jsonify({
            "response": result.strip(),
            "session_id": session_id
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
