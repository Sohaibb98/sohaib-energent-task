#!/usr/bin/env python3
"""
Test script to verify agent can run in computer-use-demo container
"""

import asyncio
import json
import sys
import os

# Set up environment
os.environ["DISPLAY"] = ":1"
os.environ["WIDTH"] = "1024"
os.environ["HEIGHT"] = "768"
os.environ["PATH"] = "/usr/bin:/usr/local/bin:" + os.environ.get("PATH", "")

try:
    from computer_use_demo.loop import APIProvider, sampling_loop
    from computer_use_demo.tools import ToolResult, ToolVersion
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

async def test_agent():
    """Test the agent with a message from environment variable"""
    
    # Get message from environment variable
    agent_message = os.environ.get("AGENT_MESSAGE", "Take a screenshot of the desktop")
    
    messages = [
        {
            "role": "user",
            "content": [{"type": "text", "text": agent_message}]
        }
    ]
    
    def output_callback(content_block):
        if content_block.get('type') == 'text':
            print(json.dumps({'type': 'output', 'content': content_block['text']}))
    
    def tool_output_callback(tool_result, tool_id):
        print(json.dumps({
            'type': 'tool_output', 
            'tool_id': tool_id, 
            'output': tool_result.output, 
            'error': tool_result.error
        }))
    
    def api_response_callback(request, response, error):
        if error:
            print(json.dumps({'type': 'api_error', 'error': str(error)}))
    
    api_key = "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"
    
    try:
        await sampling_loop(
            model='claude-sonnet-4-20250514',
            provider=APIProvider.ANTHROPIC,
            system_prompt_suffix='',
            messages=messages,
            output_callback=output_callback,
            tool_output_callback=tool_output_callback,
            api_response_callback=api_response_callback,
            api_key=api_key,
            only_n_most_recent_images=3,
            max_tokens=4096,
            tool_version='computer_use_20250124',
            thinking_budget=None,
            token_efficient_tools_beta=False,
        )
        print(json.dumps({'type': 'success', 'message': 'Agent completed successfully'}))
    except Exception as e:
        print(json.dumps({'type': 'error', 'error': str(e)}))

if __name__ == "__main__":
    asyncio.run(test_agent()) 