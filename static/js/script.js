// Use strict mode for better error catching and performance
'use strict';

// Use modern syntax: arrow functions, const/let instead of var
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded and parsed');
    const form = document.getElementById('summarize-form');
    console.log('Form element:', form);

    if (form) {
        form.addEventListener('submit', handleSubmit);
    } else {
        console.error('Form element not found');
    }
});

// Separate the form submission logic into its own function
async function handleSubmit(e) {
    e.preventDefault();
    console.log('Form submitted');

    const videoUrl = document.getElementById('video_url').value;
    const summaryLength = document.getElementById('summary_length').value;
    const usedModel = document.getElementById('used_model').value;
    const summaryDiv = document.getElementById('summary');

    // Clear previous content
    summaryDiv.innerHTML = '<h2>Summary</h2><div id="summary-content">Summarizing...</div>';

    try {
        const result = await submitSummarizeRequest(videoUrl, summaryLength, usedModel);
        displaySummary(result, summaryDiv);
    } catch (error) {
        console.error('Error:', error);
        summaryDiv.innerHTML += `<p>Error: ${error.message}</p>`;
    }
}

// Separate API call into its own function
async function submitSummarizeRequest(videoUrl, summaryLength, usedModel) {
    const response = await fetch('/summarize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            video_url: videoUrl,
            summary_length: parseInt(summaryLength, 10),
            used_model: usedModel
        }),
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'An error occurred while summarizing the video.');
    }

    return response.json();
}

// Separate display logic into its own function
function displaySummary(result, summaryDiv) {
    if ('summary' in result && 'word_count' in result) {
        const summaryContent = document.getElementById('summary-content');
        // Split the summary into paragraphs
        const paragraphs = result.summary.split('\n\n');
        summaryContent.innerHTML = paragraphs.map(p => `<p>${p}</p>`).join('');

        // Add word count
        const wordCountElem = document.createElement('p');
        wordCountElem.id = 'word-count';
        wordCountElem.textContent = `Word count: ${result.word_count}`;
        summaryDiv.appendChild(wordCountElem);
    } else {
        summaryDiv.innerHTML += '<p>Summary or word count not available in the response.</p>';
    }
}