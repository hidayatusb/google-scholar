import streamlit as st
from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Google Scholar Dosen Statistika",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .professor-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        margin-bottom: 20px;
        border-left: 5px solid #ff6b6b;
    }
    .professor-card h3 {
        margin: 0 0 10px 0;
        font-size: 20px;
    }
    .professor-card .subtitle {
        font-size: 13px;
        opacity: 0.9;
        margin-bottom: 15px;
    }
    .stats-row {
        display: flex;
        gap: 10px;
        margin-top: 12px;
        flex-wrap: wrap;
    }
    .stat-badge {
        background: rgba(255, 255, 255, 0.2);
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    .stat-badge strong {
        display: block;
        font-size: 16px;
        margin-bottom: 3px;
    }
    .interests-box {
        background: rgba(255, 255, 255, 0.1);
        padding: 10px;
        border-radius: 6px;
        font-size: 12px;
        margin-top: 10px;
        border-left: 3px solid #ffd700;
    }
    .summary-stats {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
    }
    .summary-stats h3 {
        margin-top: 0;
        font-size: 28px;
    }
    .last-sync {
        font-size: 12px;
        color: #666;
        text-align: right;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Data dosen
PROFESSORS = {
    "Prof. 1": "https://scholar.google.com/citations?user=Jq2gTx4AAAAJ&hl=en",
    "Prof. 2": "https://scholar.google.com/citations?user=rtyWLLQAAAAJ&hl=en",
    "Prof. 3": "https://scholar.google.com/citations?user=m2Bp0jIAAAAJ&hl=id",
    "Prof. 4": "https://scholar.google.com/citations?user=cLgdVt0AAAAJ&hl=id",
    "Prof. 5": "https://scholar.google.com/citations?user=cKRYwyQAAAAJ&hl=en",
    "Prof. 6": "https://scholar.google.com/citations?user=VkiMg2MAAAAJ&hl=en",
    "Prof. 7": "https://scholar.google.com/citations?user=4AY3GH8AAAAJ&hl=en",
}

def scrape_scholar_profile(url):
    """Scrape Google Scholar profile information"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extracting profile information
        name_element = soup.find('div', id='gsc_prf_in')
        name = name_element.text.strip() if name_element else "Name not found"
        
        # Try to get h-index and citations from the page
        stats = {}
        stat_elements = soup.find_all('td', class_='gsc_rsb_std')
        if len(stat_elements) >= 3:
            stats['citations'] = stat_elements[0].text if stat_elements[0] else "-"
            stats['h_index'] = stat_elements[3].text if stat_elements[3] else "-"
            stats['i10_index'] = stat_elements[5].text if stat_elements[5] else "-"
        else:
            stats['citations'] = "-"
            stats['h_index'] = "-"
            stats['i10_index'] = "-"
        
        affiliation_elements = soup.find_all('div', class_='gsc_prf_il')
        affiliation = affiliation_elements[0].text.strip() if affiliation_elements else "Affiliation not found"
        
        interests = [interest.text.strip() for interest in soup.find_all('a', class_='gsc_prf_inta')]
        interests_str = ', '.join(interests[:5]) if interests else "No interests found"
        
        return {
            'name': name,
            'affiliation': affiliation,
            'interests': interests_str,
            'citations': stats.get('citations', '-'),
            'h_index': stats.get('h_index', '-'),
            'i10_index': stats.get('i10_index', '-'),
            'url': url,
            'success': True
        }
    except Exception as e:
        return {
            'name': 'Error',
            'affiliation': str(e),
            'interests': '-',
            'citations': '-',
            'h_index': '-',
            'i10_index': '-',
            'url': url,
            'success': False
        }

def scrape_all_profiles():
    """Scrape all professor profiles"""
    results = {}
    for prof_name, prof_url in PROFESSORS.items():
        results[prof_name] = scrape_scholar_profile(prof_url)
    return results

def display_professor_card(prof_name, data):
    """Display professor profile card with Streamlit components"""
    st.markdown(f"### 👨‍🏫 {data['name']}")


    stat_cols = st.columns(3)
    stat_cols[0].metric("Citations", data['citations'])
    stat_cols[1].metric("H-Index", data['h_index'])
    stat_cols[2].metric("i10-Index", data['i10_index'])

    st.write(f"**Affiliation:** {data['affiliation']}")
    st.write(f"**Research Interests:** {data['interests']}")
    st.markdown(f"[📊 View Full Profile on Google Scholar]({data['url']})")


def initialize_session_state():
    """Initialize session state for storing profile data"""
    if 'profiles_data' not in st.session_state:
        st.session_state.profiles_data = {}
        st.session_state.last_sync = None

def main():
    # Initialize session state
    initialize_session_state()
    
    # Header with Sync button
    col1, col2 = st.columns([6, 1])
    
    with col1:
        st.markdown("# 🎓 Google Scholar Dosen Statistika")
    
    with col2:
        st.write("")  # spacing
        if st.button("🔄 Sync", key="sync_btn", use_container_width=True):
            with st.spinner("Syncing all profiles..."):
                st.session_state.profiles_data = scrape_all_profiles()
                st.session_state.last_sync = datetime.now()
                st.rerun()
    
    # Auto-scrape on first load
    if not st.session_state.profiles_data:
        st.info("⏳ Loading professor data...")
        with st.spinner("Scraping Google Scholar profiles..."):
            st.session_state.profiles_data = scrape_all_profiles()
            st.session_state.last_sync = datetime.now()
            st.rerun()
    
    st.divider()
    
    # Display last sync time
    if st.session_state.last_sync:
        st.markdown(f'<div class="last-sync">Last synced: {st.session_state.last_sync.strftime("%Y-%m-%d %H:%M:%S")}</div>', 
                   unsafe_allow_html=True)
    
    # Display all profiles in a grid (2 columns)
    st.markdown("### 📋 Dosen Profiles")
    
    # Filter successful profiles
    successful_profiles = {
        prof: data for prof, data in st.session_state.profiles_data.items() 
        if data['success']
    }
    
    if successful_profiles:
        # Create columns for grid layout
        cols = st.columns(2)
        for idx, (prof_name, data) in enumerate(successful_profiles.items()):
            with cols[idx % 2]:
                display_professor_card(prof_name, data)
                st.markdown("---")
    else:
        st.warning("No successful profiles loaded. Click Sync to try again.")
    
    # Summary section
    st.divider()
    st.markdown("### 📊 Summary Statistics")
    
    if successful_profiles:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_citations = sum([
                int(p['citations'].replace(',', '')) if p['citations'] != '-' else 0 
                for p in successful_profiles.values()
            ])
            st.metric("📈 Total Citations", total_citations)
        
        with col2:
            total_profiles = len(successful_profiles)
            st.metric("👥 Active Profiles", total_profiles)
        
        with col3:
            avg_h_index = sum([
                int(p['h_index']) if p['h_index'] != '-' else 0 
                for p in successful_profiles.values()
            ]) / len(successful_profiles) if successful_profiles else 0
            st.metric("📊 Avg H-Index", f"{avg_h_index:.1f}")
        
        with col4:
            avg_i10 = sum([
                int(p['i10_index']) if p['i10_index'] != '-' else 0 
                for p in successful_profiles.values()
            ]) / len(successful_profiles) if successful_profiles else 0
            st.metric("🏆 Avg i10-Index", f"{avg_i10:.1f}")
    else:
        st.info("Load profiles to see statistics")

if __name__ == "__main__":
    main()