class AutocompleteSearch {
    constructor(inputId, suggestionsId, errorId, selectedId, fighterKey) {
        this.input = document.getElementById(inputId);
        this.suggestions = document.getElementById(suggestionsId);
        this.errorDiv = document.getElementById(errorId);
        this.selectedDiv = document.getElementById(selectedId);
        this.fighterKey = fighterKey;
        this.selectedFighter = null;
        this.currentFocus = -1;
        this.suggestionsList = [];
        
        this.init();
    }
    
    init() {
        // Input event with debouncing
        let timeout;
        this.input.addEventListener('input', (e) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => this.handleInput(e), 250);
        });
        
        // Keyboard navigation
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.autocomplete-container')) {
                this.hideSuggestions();
            }
        });
    }
    
    async handleInput(e) {
        const query = e.target.value.trim();
        this.hideError();
        
        // Clear selection if user types something different
        if (this.selectedFighter && query !== this.selectedFighter) {
            this.clearSelection();
        }
        
        if (query.length == 0) {
            this.hideSuggestions();
            return;
        }
        
        try {
            const response = await fetch(`/search_fighters?q=${encodeURIComponent(query)}`);
            const fighters = await response.json();
            this.showSuggestions(fighters);
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Search failed. Please try again.');
        }
    }
    
    handleKeydown(e) {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            this.currentFocus++;
            this.updateFocus();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            this.currentFocus--;
            this.updateFocus();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            this.handleEnter();
        } else if (e.key === 'Escape') {
            this.hideSuggestions();
            this.input.blur();
        }
    }
    
    handleEnter() {
        if (this.suggestionsList.length === 0) {
            // No matches found
            this.showError('Could not find any fighters matching your search, try again');
            this.input.value = '';
            return;
        }
        
        // Select the focused item, or first item if none focused
        const indexToSelect = this.currentFocus >= 0 ? this.currentFocus : 0;
        if (this.suggestionsList[indexToSelect]) {
            this.selectFighter(this.suggestionsList[indexToSelect]);
        }
    }
    
    showSuggestions(fighters) {
        this.suggestionsList = fighters;
        this.suggestions.innerHTML = '';
        
        if (fighters.length === 0) {
            this.hideSuggestions();
            return;
        }
        
        fighters.forEach((fighter, index) => {
            const li = document.createElement('li');
            li.textContent = fighter;
            li.addEventListener('click', () => this.selectFighter(fighter));
            li.addEventListener('mouseenter', () => {
                this.currentFocus = index;
                this.updateFocus();
            });
            this.suggestions.appendChild(li);
        });
        
        this.suggestions.style.display = 'block';
        this.currentFocus = -1;
    }
    
    updateFocus() {
        const items = this.suggestions.querySelectorAll('li');
        
        // Remove previous focus
        items.forEach(item => item.style.backgroundColor = '');
        
        // Add focus to current item
        if (this.currentFocus >= 0 && this.currentFocus < items.length) {
            items[this.currentFocus].style.backgroundColor = '#f0f0f0';
        } else if (this.currentFocus >= items.length) {
            this.currentFocus = 0;
            if (items.length > 0) items[0].style.backgroundColor = '#f0f0f0';
        } else if (this.currentFocus < 0) {
            this.currentFocus = items.length - 1;
            if (items.length > 0) items[this.currentFocus].style.backgroundColor = '#f0f0f0';
        }
    }
    
    selectFighter(fighter) {
        this.selectedFighter = fighter;
        this.input.value = fighter;
        this.hideSuggestions();
        this.hideError();
        this.selectedDiv.querySelector('span').textContent = fighter;
        this.selectedDiv.style.display = 'block';
        
        // Update submit button state
        updateSubmitButton();
    }
    
    clearSelection() {
        this.selectedFighter = null;
        this.selectedDiv.style.display = 'none';
        updateSubmitButton();
    }
    
    hideSuggestions() {
        this.suggestions.style.display = 'none';
        this.currentFocus = -1;
    }
    
    showError(message) {
        this.errorDiv.textContent = message;
        this.errorDiv.style.display = 'block';
        setTimeout(() => this.hideError(), 3000);
    }
    
    hideError() {
        this.errorDiv.style.display = 'none';
    }
    
    getSelected() {
        return this.selectedFighter;
    }
}

// Initialize autocomplete search bars
const fighter1Search = new AutocompleteSearch(
    'fighter1-input', 'fighter1-suggestions', 'fighter1-error', 'fighter1-selected', 'fighter1'
);
const fighter2Search = new AutocompleteSearch(
    'fighter2-input', 'fighter2-suggestions', 'fighter2-error', 'fighter2-selected', 'fighter2'
);

// Submit button functionality
function updateSubmitButton() {
    const submitBtn = document.getElementById('submit-btn');
    const hasValidSelection = fighter1Search.getSelected() && fighter2Search.getSelected();
    submitBtn.disabled = !hasValidSelection;
}

document.getElementById('submit-btn').addEventListener('click', async () => {
    const fighter1 = fighter1Search.getSelected();
    const fighter2 = fighter2Search.getSelected();
    
    if (!fighter1 || !fighter2) return;
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fighter1, fighter2 })
        });
        
        const result = await response.json();
        const resultDiv = document.getElementById('result');
        
        if (response.ok) {
            //         result = {
            // "winner": r.fighter if (pred[0] == 1) else b.fighter,
            // "rprob": round(r_p, 4),
            // "bprob": round(b_p, 4),
            // "rcorner": r.fighter,
            // "bcorner": b.fighter
            resultDiv.innerHTML = `
                <p>Red Corner: ${result.rcorner}, Blue Corner: ${result.bcorner}</p>
                <p>Probabilities: [${result.rprob}, ${result.bprob}]</p>
                <p>Winner: ${result.winner}</p>
            `;
        } else {
            resultDiv.innerHTML = `<p style="color: red;">Error: ${result.error}</p>`;
        }
    } catch (error) {
        document.getElementById('result').innerHTML = '<p style="color: red;">Network error occurred</p>';
    }
});