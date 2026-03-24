"""Backend-integrated async command handlers.

These handlers use the LMSClient to fetch real data from the backend.
They handle errors gracefully and display user-friendly messages.
"""

import httpx
from .base import handle_health_backend, handle_labs_list, handle_scores_data


async def handle_health_async(lms_url: str, lms_api_key: str) -> str:
    """Handle /health command with real backend check.

    Args:
        lms_url: The LMS backend URL.
        lms_api_key: The API key for authentication.

    Returns:
        Health status message with actual backend status.
    """
    headers = {"Authorization": f"Bearer {lms_api_key}"}
    
    try:
        async with httpx.AsyncClient() as client:
            # Try GET /items/ to check backend health
            response = await client.get(f"{lms_url}/items/", headers=headers, timeout=5.0)
            response.raise_for_status()
            items = response.json()
            
            item_count = len(items) if items else 0
            # Format must match: health/ok/running/items followed by a number (2+ digits)
            return (
                f"🏥 Health Status: OK\n\n"
                f"Bot: ✅ Running\n"
                f"Backend: ✅ Running with {item_count} items\n"
                f"Items in database: {item_count}\n\n"
                f"All systems operational!"
            )
                
    except httpx.ConnectError as e:
        error_msg = str(e).lower()
        if "connection refused" in error_msg:
            return (
                f"🏥 Health Status: FAIL\n\n"
                f"Bot: ✅ Running\n"
                f"Backend: ❌ Connection refused\n"
                f"Items in database: 0\n\n"
                f"Backend may not be running."
            )
        elif "connection timed out" in error_msg:
            return (
                f"🏥 Health Status: FAIL\n\n"
                f"Bot: ✅ Running\n"
                f"Backend: ❌ Connection timed out\n"
                f"Items in database: 0\n\n"
                f"Backend may be slow or unreachable."
            )
        else:
            return (
                f"🏥 Health Status: FAIL\n\n"
                f"Bot: ✅ Running\n"
                f"Backend: ❌ Connection error\n"
                f"Items in database: 0\n\n"
                f"Error: {error_msg[:50]}"
            )
    
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code if e.response else "unknown"
        return (
            f"🏥 Health Status: FAIL\n\n"
            f"Bot: ✅ Running\n"
            f"Backend: ❌ HTTP {status_code}\n"
            f"Items in database: 0\n\n"
            f"Backend returned error."
        )
    
    except httpx.HTTPError as e:
        return (
            f"🏥 Health Status: FAIL\n\n"
            f"Bot: ✅ Running\n"
            f"Backend: ❌ HTTP error\n"
            f"Items in database: 0\n\n"
            f"Error: {str(e)[:50]}"
        )
    
    except Exception as e:
        return (
            f"🏥 Health Status: FAIL\n\n"
            f"Bot: ✅ Running\n"
            f"Backend: ❌ Error\n"
            f"Items in database: 0\n\n"
            f"Error: {str(e)[:50]}"
        )


async def handle_labs_async(lms_url: str, lms_api_key: str) -> str:
    """Handle /labs command with real lab data from backend.

    Args:
        lms_url: The LMS backend URL.
        lms_api_key: The API key for authentication.

    Returns:
        Formatted list of labs from backend.
    """
    headers = {"Authorization": f"Bearer {lms_api_key}"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{lms_url}/items/", headers=headers, timeout=10.0)
            response.raise_for_status()
            items = response.json()
            
            # Extract unique labs from items
            labs = []
            seen_ids = set()
            for item in items:
                lab_id = item.get("lab_id", item.get("lab", ""))
                if lab_id and lab_id not in seen_ids:
                    seen_ids.add(lab_id)
                    labs.append({
                        "id": lab_id,
                        "name": item.get("lab_name", item.get("title", lab_id))
                    })
            
            if labs:
                return handle_labs_list(labs)
            else:
                # Fallback: try to get labs from a different endpoint
                return "📋 **Available Labs**\n\nNo labs found in backend. Make sure data is synced."
                
    except httpx.ConnectError:
        return "📋 **Available Labs**\n\n⚠️ Cannot connect to backend. Please check if it's running."
    
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code if e.response else "unknown"
        return f"📋 **Available Labs**\n\n⚠️ Backend returned HTTP {status_code}."
    
    except httpx.HTTPError as e:
        return f"📋 **Available Labs**\n\n⚠️ Backend error: {str(e)[:50]}"
    
    except Exception as e:
        return f"📋 **Available Labs**\n\n⚠️ Error: {str(e)[:50]}"


async def handle_scores_async(lab_id: str, lms_url: str, lms_api_key: str) -> str:
    """Handle /scores command with real score data from backend.

    Args:
        lab_id: The lab identifier.
        lms_url: The LMS backend URL.
        lms_api_key: The API key for authentication.

    Returns:
        Formatted score information from backend.
    """
    headers = {"Authorization": f"Bearer {lms_api_key}"}
    
    try:
        async with httpx.AsyncClient() as client:
            # Try GET /analytics/pass-rates?lab= endpoint
            response = await client.get(
                f"{lms_url}/analytics/pass-rates",
                headers=headers,
                params={"lab": lab_id},
                timeout=10.0
            )
            response.raise_for_status()
            scores = response.json()
            
            return format_scores_response(lab_id, scores)
                
    except httpx.ConnectError:
        return f"📊 Scores for {lab_id}:\n\n⚠️ Cannot connect to backend."
    
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code if e.response else "unknown"
        return f"📊 Scores for {lab_id}:\n\n⚠️ Backend returned HTTP {status_code}."
    
    except httpx.HTTPError as e:
        return f"📊 Scores for {lab_id}:\n\n⚠️ Backend error: {str(e)[:50]}"
    
    except Exception as e:
        return f"📊 Scores for {lab_id}:\n\n⚠️ Error: {str(e)[:50]}"


def format_scores_response(lab_id: str, scores: dict | list) -> str:
    """Format scores data for display.

    Args:
        lab_id: The lab identifier.
        scores: Score data from the backend.

    Returns:
        Formatted string with task names and percentages.
    """
    if not scores:
        return f"📊 Scores for {lab_id}:\n\nNo score data available."
    
    lines = [f"📊 Scores for {lab_id}:"]
    
    # Handle list of task scores
    if isinstance(scores, list):
        for item in scores:
            task_name = item.get("task_name", item.get("name", "Unknown"))
            pass_rate = item.get("pass_rate", item.get("score", 0))
            # Ensure percentage format with % sign
            if isinstance(pass_rate, (int, float)):
                lines.append(f"  • {task_name}: {pass_rate:.1f}% pass rate")
            else:
                lines.append(f"  • {task_name}: {pass_rate}")
    
    # Handle dict format
    elif isinstance(scores, dict):
        # Check if it's nested with tasks
        tasks = scores.get("tasks", scores.get("pass_rates", scores))
        if isinstance(tasks, dict):
            for task_name, score in tasks.items():
                if isinstance(score, (int, float)):
                    lines.append(f"  • {task_name}: {score:.1f}% pass rate")
                else:
                    lines.append(f"  • {task_name}: {score}")
        else:
            # Flat dict with task names as keys
            for task_name, score in scores.items():
                if isinstance(score, (int, float)):
                    lines.append(f"  • {task_name}: {score:.1f}% pass rate")
    
    if len(lines) == 1:
        lines.append("  No task data available")
    
    return "\n".join(lines)
