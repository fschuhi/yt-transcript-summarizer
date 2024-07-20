'use strict';

let accessToken = null;

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

async function login() {
    const apiKey = prompt("Enter your API key:");
    if (!apiKey) return false;

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'X-API-Key': apiKey
            }
        });

        if (response.ok) {
            const data = await response.json();
            accessToken = data.access_token;
            return true;
        } else {
            alert("Invalid API key");
            return false;
        }
    } catch (error) {
        console.error('Login error:', error);
        return false;
    }
}

async function handleSubmit(e) {
    e.preventDefault();
    console.log('Form submitted');

    if (!accessToken) {
        const loggedIn = await login();
        console.log()
        if (!loggedIn) return;
    }

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

async function submitSummarizeRequest(videoUrl, summaryLength, usedModel) {
    const response = await fetch('/summarize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': accessToken
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