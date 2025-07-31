document.getElementById('researchForm').addEventListener('submit', async function(e) {
    console.log("main.js loaded!");
    e.preventDefault();
    const query = document.getElementById('query').value.trim();
    if (!query) return;

    const conversation = document.getElementById('conversation');
    const userBlock = document.createElement('div');
    userBlock.className = 'block user';
    userBlock.textContent = 'You: ' + query;
    conversation.appendChild(userBlock);

    const assistantBlock = document.createElement('div');
    assistantBlock.className = 'block assistant';
    assistantBlock.innerHTML = "<em>Processing...</em>";
    conversation.appendChild(assistantBlock);


    conversation.scrollTop = conversation.scrollHeight;

  
    document.getElementById('query').value = "";

    try {
        const response = await fetch('http://127.0.0.1:5500/research', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
});

        if (response.ok) {
            const data = await response.json();
            assistantBlock.innerHTML = `
                <strong>Assistant:</strong>
                <div>
                    <b>Topic:</b> ${data.topic || 'N/A'}<br>
                    <b>Summary:</b> ${data.summary || 'N/A'}<br>
                    <b>Sources:</b> <ul>${Array.isArray(data.sources) ? data.sources.map(src => `<li>${src}</li>`).join('') : ''}</ul>
                    <b>Tools Used:</b> <ul>${Array.isArray(data.tools_used) ? data.tools_used.map(tool => `<li>${tool}</li>`).join('') : ''}</ul>
                </div>
            `;
        } else {
            const errorText = await response.text();
            assistantBlock.innerHTML = `<span style='color:red'>Server error: ${response.status} - ${errorText}</span>`;
        }
    } catch (err) {
        assistantBlock.innerHTML = `<span style='color:red'>Error: ${err.message}</span>`;
    }


    conversation.scrollTop = conversation.scrollHeight;
});