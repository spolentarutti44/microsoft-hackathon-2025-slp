document.addEventListener('DOMContentLoaded', function() {
    // Helper to format content into HTML string
    function formatContent(content) {
        if (typeof content === 'string') return content;
        if (Array.isArray(content)) {
            return content.map(item => `<p>${item}</p>`).join('');
        }
        // Fallback: stringify object with line breaks
        try {
            const str = JSON.stringify(content, null, 2);
            return str.replace(/\n/g, '<br>');
        } catch {
            return String(content);
        }
    }
    
    // Initialize Quill editors for each section
    const editors = {
        executiveSummary: new Quill('#executive-summary-editor', { theme: 'snow', placeholder: 'Executive Summary content...' }),
        problemStatement: new Quill('#problem-statement-editor', { theme: 'snow', placeholder: 'Problem Statement content...' }),
        projectDescription: new Quill('#project-description-editor', { theme: 'snow', placeholder: 'Project Description content...' }),
        goalsObjectives: new Quill('#goals-objectives-editor', { theme: 'snow', placeholder: 'Goals & Objectives content...' }),
        implementation: new Quill('#implementation-editor', { theme: 'snow', placeholder: 'Implementation Plan content...' }),
        evaluation: new Quill('#evaluation-editor', { theme: 'snow', placeholder: 'Evaluation & Impact content...' }),
        sustainability: new Quill('#sustainability-editor', { theme: 'snow', placeholder: 'Sustainability Plan content...' }),
        conclusion: new Quill('#conclusion-editor', { theme: 'snow', placeholder: 'Conclusion content...' })
    };
    
    // Track budget items
    let budgetItems = [];
    
    // Elements
    const loadingMessage = document.getElementById('loading-message');
    const editorContainer = document.getElementById('editor-container');
    const saveDocxBtn = document.getElementById('save-docx');
    const budgetItemsContainer = document.getElementById('budget-items');
    const budgetTotal = document.getElementById('budget-total');
    const addBudgetItemBtn = document.getElementById('add-budget-item');
    const saveBudgetItemBtn = document.getElementById('save-budget-item');
    const budgetItemModal = new bootstrap.Modal(document.getElementById('budgetItemModal'));
    
    // Organization info elements
    const orgName = document.getElementById('org-name');
    const orgMission = document.getElementById('org-mission');
    const orgWebsite = document.getElementById('org-website');
    
    // Poll the server for grant status
    async function checkStatus() {
        console.log('Checking grant status...');
        try {
            const response = await fetch('http://127.0.0.1:5000/api/get-grant-status');
            const data = await response.json();
            console.log('Status response:', data);
            if (data.status === 'completed') {
                console.log('Grant generation completed, data:', data.data);
                loadingMessage.classList.add('d-none');
                editorContainer.classList.remove('d-none');
                loadGrantData(data.data);
            } else {
                setTimeout(checkStatus, 5000);
            }
        } catch (error) {
            console.error('Error checking status:', error);
            loadingMessage.textContent = 'Error loading grant application. Please try again.';
        }
    }
    
    // Function to load grant data into editors
    function loadGrantData(data) {
        console.log('Loading grant data into editors:', data);
        // Set organization info
        const orgInfo = data.organization_info || {};
        orgName.textContent = orgInfo.name || 'N/A';
        orgMission.textContent = orgInfo.mission || 'N/A';
        orgWebsite.textContent = orgInfo.website || 'N/A';
        orgWebsite.href = orgInfo.website || '#';
        
        // Set editor contents with content formatting
        // Insert HTML into Quill editor
        const execHtml = formatContent(data.executive_summary || data['Executive Summary'] || '');
        editors.executiveSummary.root.innerHTML = execHtml;
        const probHtml = formatContent(data.problem_statement || data['Problem Statement'] || '');
        editors.problemStatement.root.innerHTML = probHtml;
        const projHtml = formatContent(data.project_description || data['Project Description'] || '');
        editors.projectDescription.root.innerHTML = projHtml;
        
        // Goals & Objectives
        const goalsData = data.goals_objectives || data['Goals and Objectives'] || '';
        const goalsHtml = formatContent(goalsData);
        editors.goalsObjectives.root.innerHTML = goalsHtml;
        
        const implHtml = formatContent(data.implementation_plan || data['Implementation Plan'] || '');
        editors.implementation.root.innerHTML = implHtml;
        const evalHtml = formatContent(data.evaluation || data['Evaluation and Impact'] || '');
        editors.evaluation.root.innerHTML = evalHtml;
        const sustHtml = formatContent(data.sustainability || data['Sustainability Plan'] || '');
        editors.sustainability.root.innerHTML = sustHtml;
        const conclHtml = formatContent(data.conclusion || data['Conclusion'] || '');
        editors.conclusion.root.innerHTML = conclHtml;
        
        // Handle budget - support array or object
        if (data.budget) {
            if (Array.isArray(data.budget)) {
                budgetItems = data.budget;
            } else if (typeof data.budget === 'object') {
                // convert object of {item: amount} to array
                budgetItems = Object.entries(data.budget).map(([item, amount]) => ({
                    item,
                    description: '',
                    amount: amount
                }));
            }
            renderBudgetItems();
        }
    }
    
    // Function to render budget items in the table
    function renderBudgetItems() {
        // Clear existing items
        budgetItemsContainer.innerHTML = '';
        
        // Calculate total
        let total = 0;
        
        // Add each budget item to the table
        budgetItems.forEach((item, index) => {
            const amount = parseFloat(item.amount) || 0;
            total += amount;
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.item}</td>
                <td>${item.description}</td>
                <td>$${amount.toFixed(2)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-danger remove-budget-item" data-index="${index}">
                        <i class="bi bi-trash"></i> Remove
                    </button>
                </td>
            `;
            budgetItemsContainer.appendChild(row);
        });
        
        // Update total
        budgetTotal.textContent = `$${total.toFixed(2)}`;
        
        // Add event listeners to remove buttons
        document.querySelectorAll('.remove-budget-item').forEach(button => {
            button.addEventListener('click', function() {
                const index = parseInt(this.getAttribute('data-index'));
                budgetItems.splice(index, 1);
                renderBudgetItems();
            });
        });
    }
    
    // Handle add budget item
    addBudgetItemBtn.addEventListener('click', function() {
        // Clear form
        document.getElementById('budget-item-name').value = '';
        document.getElementById('budget-item-description').value = '';
        document.getElementById('budget-item-amount').value = '';
        
        // Show modal
        budgetItemModal.show();
    });
    
    // Handle save budget item
    saveBudgetItemBtn.addEventListener('click', function() {
        const itemName = document.getElementById('budget-item-name').value;
        const itemDescription = document.getElementById('budget-item-description').value;
        const itemAmount = document.getElementById('budget-item-amount').value;
        
        // Validate inputs
        if (!itemName || !itemDescription || !itemAmount) {
            alert('Please fill out all fields');
            return;
        }
        
        // Add to budget items
        budgetItems.push({
            item: itemName,
            description: itemDescription,
            amount: itemAmount
        });
        
        // Update display
        renderBudgetItems();
        
        // Hide modal
        budgetItemModal.hide();
    });
    
    // Handle save as DOCX
    saveDocxBtn.addEventListener('click', function() {
        // Collect all the content
        const content = {
            title: `Grant Application for ${orgName.textContent}`,
            organization_info: {
                name: orgName.textContent,
                mission: orgMission.textContent,
                website: orgWebsite.textContent
            },
            executive_summary: editors.executiveSummary.root.innerHTML,
            problem_statement: editors.problemStatement.root.innerHTML,
            project_description: editors.projectDescription.root.innerHTML,
            goals_objectives: editors.goalsObjectives.root.innerHTML,
            implementation_plan: editors.implementation.root.innerHTML,
            evaluation: editors.evaluation.root.innerHTML,
            budget: budgetItems,
            sustainability: editors.sustainability.root.innerHTML,
            conclusion: editors.conclusion.root.innerHTML
        };
        
        // Call the API to generate the DOCX
        fetch('http://127.0.0.1:5000/api/save-grant', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content })
        })
        .then(response => {
            if (response.ok) {
                return response.blob();
            }
            throw new Error('Network response was not ok');
        })
        .then(blob => {
            // Create a download link and trigger it
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'grant_application.docx';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error('Error saving document:', error);
            alert('Error saving document. Please try again.');
        });
    });
    
    // Start checking status when page loads
    checkStatus();
}); 