let listenButton = document.getElementById('listenButton');
let clearButton = document.getElementById('clearButton');
let questionsArea = document.getElementById('questionsArea');
let answersArea = document.getElementById('answersArea');
let apiKeyInput = document.getElementById('apiKeyInput');
let saveApiKeyButton = document.getElementById('saveApiKey');
let deleteApiKeyButton = document.getElementById('deleteApiKey');
let modal = document.getElementById('modal');
let modalMessage = document.getElementById('modal-message');
let closeModal = document.getElementsByClassName('close')[0];
let modalLogo = document.getElementById('modal-logo');

// Add these lines at the beginning of your script
let logoContainer = document.querySelector('.logo-container');
let closeLogo = document.querySelector('.close-logo');

// Add this event listener for the close logo button
closeLogo.addEventListener('click', () => {
    logoContainer.classList.add('logo-hidden');
});

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded and parsed');

    // Select the elements after the DOM is loaded
    const logoContainer = document.querySelector('.logo-container');
    const closeLogo = document.querySelector('.close-logo');

    // Log element references for debugging
    console.log('Logo Container:', logoContainer);
    console.log('Close Logo Element:', closeLogo);

    // Verify and set up close functionality
    if (closeLogo) {
        closeLogo.addEventListener('click', () => {
            logoContainer.classList.add('logo-hidden');
            console.log('Close logo clicked');
        });
    } else {
        console.error('Close logo element not found');
    }
});
// document.addEventListener('DOMContentLoaded', () => {
//     console.log('DOM fully loaded and parsed');

//     // Modal handling with comprehensive error checking
//     try {
//         const modal = document.getElementById('modal');
//         const closeLogo = modal ? modal.querySelector('.close') : null;
//         const modalLogo = document.getElementById('modal-logo');
//         const modalMessage = document.getElementById('modal-message');

//         // Log element references for debugging
//         console.log('Modal Element:', modal);
//         console.log('Close Logo Element:', closeLogo);
//         console.log('Modal Logo Element:', modalLogo);
//         console.log('Modal Message Element:', modalMessage);

//         // Verify and set up close functionality
//         if (closeLogo) {
//             closeLogo.addEventListener('click', (event) => {
//                 event.preventDefault();
//                 console.log('Close logo clicked');
//                 if (modal) {
//                     modal.style.display = 'none';
//                 }
//             });
//         } else {
//             console.error('Close logo element not found');
//         }
//     } catch (error) {
//         console.error('Error setting up modal functionality:', error);
//     }
// });

// Check for existing API key on load
window.addEventListener('load', async () => {
    const hasApiKey = await eel.has_api_key()();
    updateApiKeyUI(hasApiKey);
});

listenButton.addEventListener('click', async () => {
    let isListening = await eel.toggle_listening()();
    listenButton.textContent = isListening ? 'Stop Listening' : 'Start Listening';
    listenButton.classList.toggle('listening', isListening);
    
    if (isListening) {
        let spinner = document.createElement('div');
        spinner.className = 'spinner';
        listenButton.appendChild(spinner);
    }
});

clearButton.addEventListener('click', () => {
    questionsArea.innerHTML = '';
    answersArea.innerHTML = '';
});

saveApiKeyButton.addEventListener('click', async () => {
    const apiKey = apiKeyInput.value.trim();
    if (apiKey) {
        const result = await eel.save_api_key(apiKey)();
        if (result) {
            showModal('Open AI API key saved successfully!', 'OpenAI_Logo.png');
            apiKeyInput.value = '';
            updateApiKeyUI(true);
        } else {
            showModal('Failed to save API key. Please try again.');
        }
    } else {
        showModal('Please enter a valid API key.');
    }
});

deleteApiKeyButton.addEventListener('click', async () => {
    const result = await eel.delete_api_key()();
    if (result) {
        showModal('API key removed successfully!');
        updateApiKeyUI(false);
    } else {
        showModal('Failed to delete API key. Please try again.');
    }
});

function updateApiKeyUI(hasApiKey) {
    apiKeyInput.style.display = hasApiKey ? 'none' : 'inline-block';
    saveApiKeyButton.style.display = hasApiKey ? 'none' : 'inline-block';
    deleteApiKeyButton.style.display = hasApiKey ? 'inline-block' : 'none';
    listenButton.disabled = !hasApiKey;
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded and parsed');

    // Modal handling with comprehensive error checking
    try {
        const modal = document.getElementById('modal');
        const closeLogo = modal ? modal.querySelector('.close') : null;
        const modalLogo = document.getElementById('modal-logo');
        const modalMessage = document.getElementById('modal-message');

        // Log element references for debugging
        console.log('Modal Element:', modal);
        console.log('Close Logo Element:', closeLogo);
        console.log('Modal Logo Element:', modalLogo);
        console.log('Modal Message Element:', modalMessage);

        // Remove any existing event listeners and add new one
        if (closeLogo) {
            // Remove existing click events
            const oldCloseLogo = closeLogo.cloneNode(true);
            closeLogo.parentNode.replaceChild(oldCloseLogo, closeLogo);

            // Add new click event
            oldCloseLogo.addEventListener('click', (event) => {
                event.preventDefault();
                console.log('Close logo clicked');
                if (modal) {
                    modal.style.display = 'none';
                }
            });
        } else {
            console.error('Close logo element not found');
        }

        // Function to show modal with error handling
        window.showModal = function(message, logoSrc = null) {
            try {
                if (modal && modalMessage) {
                    modalMessage.textContent = message;
                    
                    if (modalLogo) {
                        if (logoSrc) {
                            modalLogo.src = logoSrc;
                            modalLogo.style.display = 'block';
                        } else {
                            modalLogo.style.display = 'none';
                        }
                    }
                    
                    modal.style.display = 'block';
                } else {
                    console.error('Modal elements not found');
                }
            } catch (error) {
                console.error('Error showing modal:', error);
            }
        };
    } catch (error) {
        console.error('Error setting up modal functionality:', error);
    }
});

closeModal.onclick = function() {
    modal.style.display = 'none';
}

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}

eel.expose(update_ui);
function update_ui(question, answer) {
    console.log("update_ui called with:", { question, answer }); // Debug log
    console.trace("Call stack for update_ui"); // Add call stack trace

    // Ensure UI elements exist
    if (!questionsArea || !answersArea) {
        console.error("UI elements not found!");
        questionsArea = document.getElementById('questionsArea');
        answersArea = document.getElementById('answersArea');
    }

    if (question) {
        let p = document.createElement('p');
        p.textContent = question;
        questionsArea.appendChild(p);
        questionsArea.scrollTop = questionsArea.scrollHeight;
        console.log("Question added to UI:", question);
    }

    if (answer) {
        let answerContainer = document.createElement('div');
        answerContainer.className = 'answer-container';
        
        let p = document.createElement('p');
        try {
            const parsedAnswer = JSON.parse(answer);
            console.log("Parsed answer:", parsedAnswer); // Debug log
            p.textContent = parsedAnswer.text;
            
            if (parsedAnswer.audio) {
                let audio = new Audio(`data:audio/mp3;base64,${parsedAnswer.audio}`);
                audio.onplay = function() {
                    eel.audio_playback_started()();
                };
                audio.onended = function() {
                    eel.audio_playback_ended()();
                };
                
                let muteIcon = document.createElement('span');
                muteIcon.className = 'mute-icon';
                muteIcon.innerHTML = '🔊';
                muteIcon.title = 'Mute/Unmute';
                muteIcon.onclick = function() {
                    audio.muted = !audio.muted;
                    muteIcon.innerHTML = audio.muted ? '🔇' : '🔊';
                };
                
                answerContainer.appendChild(muteIcon);
                
                audio.play().catch(e => console.error("Error playing audio:", e));
            }
        } catch (e) {
            console.error("Error parsing answer:", e); // Debug log
            console.error("Raw answer received:", answer);
            p.textContent = answer;
        }
        
        answerContainer.appendChild(p);
        answersArea.appendChild(answerContainer);
        answersArea.scrollTop = answersArea.scrollHeight;
        console.log("Answer added to UI:", p.textContent);
    }
}

let ttsToggle = document.getElementById('ttsToggle');
let ttsEnabled = true;  // Set this to true by default

// Update the UI to reflect the default state
ttsToggle.classList.toggle('disabled', !ttsEnabled);

ttsToggle.addEventListener('click', async () => {
    ttsEnabled = await eel.toggle_tts()();
    ttsToggle.classList.toggle('disabled', !ttsEnabled);
});

// Add diagnostic logging for Eel integration
console.log("Checking Eel integration...");
console.log("Window.eel exists:", typeof window.eel !== 'undefined');

// Diagnostic function to test Eel exposure
async function testEelConnection() {
    try {
        console.log("Attempting to test Eel connection...");
        
        // Expose a test function to Python
        eel.expose(receiveTestMessage);
        function receiveTestMessage(message) {
            console.log("Received message from Python:", message);
        }

        // Call a test function in Python
        console.log("Calling test function in Python...");
        await eel.test_javascript_connection("Hello from JavaScript!")();
    } catch (error) {
        console.error("Error testing Eel connection:", error);
    }
}

// Call the test function when the script loads
testEelConnection();