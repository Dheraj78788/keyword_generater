async function generateKeywords() {
    const seed = document.getElementById('seedKeyword').value;
    const service = document.getElementById('service').value;
    const limit = document.getElementById('limit').value;
    
    if (!seed) return alert('Keyword daal bhai!');
    
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({seed, service, limit: parseInt(limit)})
        });
        
        const data = await response.json();
        showResults(data);
    } catch(e) {
        alert('Error! Check console.');
    }
    
    document.getElementById('loading').classList.add('hidden');
}

function showResults(data) {
    document.getElementById('totalCount').textContent = data.total;
    document.getElementById('downloadBtn').href = `/download/${data.download}`;
    
    const grid = document.getElementById('keywordsList');
    grid.innerHTML = data.keywords.map(kw => 
        `<div class="keyword-card">${kw}</div>`
    ).join('');
    
    document.getElementById('results').classList.remove('hidden');
}
