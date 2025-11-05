from typing import Dict, List, Any
import os


def build_cruise_url(results: Dict, index: int) -> str:
    """Build cruise website URL from search results."""
    base_url = os.getenv('CRUISE_BASE_URL', 'http://uat.center.cruises/cruise-')
    try:
        meta_list = results.get("metadatas", [[]])
        meta = meta_list[0][index] if meta_list and len(meta_list[0]) > index else {}

        ufl = str(meta.get("ufl", "")).strip()
        ranges_str = str(meta.get("ranges", "")).strip()

        if not ufl:
            print(f"⚠️ Missing 'ufl' for index {index}")
            return ""

        # Extract first range
        first_range = ""
        if ranges_str:
            ranges_parts = [r.strip() for r in ranges_str.split(",") if r.strip()]
            if ranges_parts:
                first_range = ranges_parts[0]

        if not first_range:
            print(f"⚠️ Missing 'ranges' for index {index}")
            return ""

        return f"{base_url}{first_range}-{ufl}"

    except Exception as e:
        print(f"❌ Failed to build cruise URL for index {index}: {e}")
        return ""


def parse_cruise_results(results: Dict) -> List[Dict[str, Any]]:
    """Parse vector database results into structured cruise data."""
    parsed_results = []
    
    for i, doc_id in enumerate(results["ids"][0]):
        cruise_url = build_cruise_url(results, i)
        parsed_result = {
            "cruise_id": doc_id,
            "cruise_info": results["documents"][0][i],
            "meta": results["metadatas"][0][i],
            "score": results["distances"][0][i],
            "link_to_website": cruise_url
        }
        parsed_results.append(parsed_result)
    
    return parsed_results
