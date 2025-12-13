document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById("aiChatModal");
    const openBtn = document.getElementById("openAIChat");
    const closeBtn = document.querySelector(".close-button");

    const chatBox = document.getElementById('modal-chat-box');
    const userInput = document.getElementById('modal-user-input');
    const sendBtn = document.getElementById('modal-send-btn');
    const contextInput = document.getElementById('modal-pokemon-context');

    let chatHistory = []; 
    const initialBotMessageText = "Como posso ajudar a manter seus Pokémon fortes e prontos para a batalha? Qual é sua dúvida?";

    function scrollToBottom() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function addMessage(text, isUser, addToHistory = true) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
        
        messageDiv.innerHTML = text.replace(/\n/g, '<br>'); 

        chatBox.appendChild(messageDiv);
        scrollToBottom();
        
        if (addToHistory) {
            const role = isUser ? "user" : "model";
            chatHistory.push({
                "role": role,
                "parts": [{"text": text}]
            });
        }
    }

    function initializeChat() {
        if (chatHistory.length === 0) {
            addMessage(initialBotMessageText, false); 
        } else {
            chatBox.innerHTML = '';
            chatHistory.forEach(msg => {
                 addMessage(msg.parts[0].text, msg.role === 'user', false); 
            });
        }
    }
    
    openBtn.onclick = function() {
        modal.style.display = "flex";
        
        contextInput.value = ''; 
        
        const detailPokemonNameElement = document.getElementById('pokemon-name');
        if (detailPokemonNameElement) {
            const pokemonName = detailPokemonNameElement.value;
            contextInput.value = pokemonName;
            
            document.getElementById('modal-title').innerText = `🩺 Enfermeira Joy: Ajuda com ${pokemonName.toUpperCase()}`;
        } else {
            document.getElementById('modal-title').innerText = `🩺 Enfermeira Joy (Assistente IA)`;
        }

        initializeChat(); 
        
        userInput.focus();
        scrollToBottom();
    }

    closeBtn.onclick = function() {
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
    
    async function sendMessage() {
        const rawPrompt = userInput.value.trim();
        if (!rawPrompt) return;

        const pokemonContext = contextInput.value;
        let aiPrompt = rawPrompt;
        
        if (pokemonContext) {
            aiPrompt = `Com foco no Pokémon ${pokemonContext}, ${rawPrompt}`;
        }

        addMessage(rawPrompt, true);
        userInput.value = '';
        sendBtn.disabled = true;
        
        const loadingMessage = document.createElement('div');
        loadingMessage.classList.add('message', 'bot-message', 'loading');
        loadingMessage.innerHTML = '🩺 Enfermeira Joy está analisando...';
        chatBox.appendChild(loadingMessage);
        scrollToBottom();

        try {
            const response = await fetch('/api/ai_chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    prompt: aiPrompt,
                    history: chatHistory 
                })
            });

            const data = await response.json();
            
            chatBox.removeChild(loadingMessage);
            
            if (data.error) {
                addMessage(`Erro da IA: ${data.error}`, false, false);
            } else {
                addMessage(data.response, false); 
            }

        } catch (error) {
            console.error('Erro ao buscar resposta da IA:', error);
            chatBox.removeChild(loadingMessage);
            addMessage('Ocorreu um erro na comunicação com a Enfermeira Joy.', false, false); 
        } finally {
            sendBtn.disabled = false;
            userInput.focus();
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});