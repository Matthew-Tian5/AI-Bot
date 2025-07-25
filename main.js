document.getElementById('researchForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const query = document.getElementById('query').value;
    document.getElementById('results').innerHTML = "<em>Processing...</em>";

    // Send query to backend using fetch
    const response = await fetch('/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
    });

    if (response.ok) {
        const data = await response.json();
        document.getElementById('results').innerHTML = `
            <h2>Topic: ${data.topic}</h2>
            <h3>Summary</h3>
            <p>${data.summary}</p>
            <h3>Sources</h3>
            <ul>${data.sources.map(src => `<li>${src}</li>`).join('')}</ul>
            <h3>Tools Used</h3>
            <ul>${data.tools_used.map(tool => `<li>${tool}</li>`).join('')}</ul>
        `;
    } else {
        const error = await response.json();
        document.getElementById('results').innerHTML = `<span style='color:red'>${error.error || "Error fetching research results."}</span>`;
    }
});