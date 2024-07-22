'use strict';

/** @type {string|null} */
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

/**
 * Prompts the user for an API key and attempts to log in.
 * @returns {Promise<boolean>} True if login was successful, false otherwise.
 */
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

/**
 * Handles the form submission event.
 * @param {Event} e - The submit event.
 */
async function handleSubmit(e) {
    e.preventDefault();
    console.log('Form submitted');

    if (!accessToken) {
        const loggedIn = await login();
        console.log()
        if (!loggedIn) return;
    }

    const videoUrl = /** @type {HTMLInputElement} */ (document.getElementById('video_url')).value;
    const summaryLength = /** @type {HTMLInputElement} */ (document.getElementById('summary_length')).value;
    const usedModel = /** @type {HTMLSelectElement} */ (document.getElementById('used_model')).value;
    const resultDiv = document.getElementById('result');

    // Clear previous content
    resultDiv.innerHTML = '<div id="loading">Summarizing...</div>';

    try {
        const result = await submitSummarizeRequest(videoUrl, summaryLength, usedModel);
        displayResult(result, resultDiv);
    } catch (error) {
        console.error('Error:', error);
        resultDiv.innerHTML = `<p>Error: ${error.message}</p>`;
    }
}

/**
 * Submits a summarize request to the server.
 * @param {string} videoUrl - The URL of the video to summarize.
 * @param {string} summaryLength - The desired length of the summary.
 * @param {string} usedModel - The model to use for summarization.
 * @returns {Promise<Object>} The summarization result.
 * @throws {Error} If the request fails.
 */
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

/**
 * Displays the summarization result in the DOM.
 * @param {Object} result - The summarization result.
 * @param {HTMLElement} resultDiv - The div to display the result in.
 */
function displayResult(result, resultDiv) {
    resultDiv.innerHTML = '';

    // Create main info box
    const mainInfoBox = createBox('main-info-box');

    // Title
    const titleElem = document.createElement('h2');
    titleElem.textContent = result.metadata.title;
    mainInfoBox.appendChild(titleElem);

    // Channel
    const channelElem = document.createElement('p');
    channelElem.innerHTML = '<span class="info-label">Channel:</span> ' + result.metadata.channel_title;
    mainInfoBox.appendChild(channelElem);

    // Short description
    const shortDescElem = document.createElement('p');
    const firstLine = result.metadata.description.split('\n')[0];
    shortDescElem.innerHTML = '<span class="info-label">Description (1st line):</span> ' + firstLine;
    mainInfoBox.appendChild(shortDescElem);

    resultDiv.appendChild(mainInfoBox);

    // Summary box
    const summaryBox = createBox('summary-box');
    summaryBox.innerHTML = '<h2>Summary</h2>';
    const summaryContent = document.createElement('div');
    summaryContent.id = 'summary-content';
    const paragraphs = result.summary.split('\n\n');
    summaryContent.innerHTML = paragraphs.map(p => `<p>${p}</p>`).join('');
    summaryBox.appendChild(summaryContent);

    // Word count
    const wordCountElem = document.createElement('p');
    wordCountElem.id = 'word-count';
    wordCountElem.textContent = `Word count: ${result.word_count}`;
    summaryBox.appendChild(wordCountElem);

    resultDiv.appendChild(summaryBox);

    // Date & counts box
    const dateCountsBox = createBox('date-counts-box');
    dateCountsBox.innerHTML = `
        <p>Published: ${new Date(result.metadata.publish_date).toLocaleDateString()}</p>
        <p>Views: ${result.metadata.view_count}</p>
        <p>Likes: ${result.metadata.like_count}</p>
        <p>Comments: ${result.metadata.comment_count}</p>
    `;
    resultDiv.appendChild(dateCountsBox);

    // Long description box
    const longDescBox = createBox('long-desc-box');
    longDescBox.innerHTML = `<p>${result.metadata.description.replace(/\n/g, '<br>')}</p>`;
    resultDiv.appendChild(longDescBox);
}

function createBox(className) {
    const box = document.createElement('div');
    box.className = `box ${className}`;
    return box;
}