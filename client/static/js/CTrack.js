// Define the initial order of options
var optionOrder = [
    { value: "Rent", text: "Rent" },
    { value: "Utilities", text: "Utilities" },
    { value: "Subscriptions", text: "Subscriptions" },
    { value: "Groceries", text: "Groceries" },
    { value: "Car Payment", text: "Car Payment" },
    { value: "Debt", text: "Debt" },
    { value: "Savings", text: "Savings" },
    { value: "Custom", text: "Custom" }
];

// Store the original index of the removed option
var removedOptionIndex = -1;


document.getElementById('add-expense-btn').addEventListener('click', function() {
    var select = document.getElementById('expense-select');
    var expenseValue = select.value;
    var expenseText = select.options[select.selectedIndex].text;
    var customExpenseInput = document.getElementById('custom-expense').value.trim();
    var expensesList = document.getElementById('expenses-list');
    var totalElement = document.getElementById('total');
    
    if (expenseValue === "" && customExpenseInput === "") {
        alert("Please select an expense and/or input a Monthly Cost.");
        return;
    }

    if (expenseValue === "Custom" && customExpenseInput === "") {
        alert("Please enter a custom expense value.");
        return;
    }

    var row = document.createElement('div');
    var expenseInfo = document.createElement('div');
    var deleteBtn = document.createElement('button');

    row.classList.add('row');

    if (expenseValue === "Custom") {
        expenseInfo.textContent = "Custom: $" + customExpenseInput;
    } else {
        expenseInfo.textContent = expenseText + ": $" + customExpenseInput;
        removeOption(expenseValue); // Remove option from dropdown if used
    }

    deleteBtn.textContent = "Delete";
    deleteBtn.classList.add('delete-btn');
    deleteBtn.addEventListener('click', function() {
        expensesList.removeChild(row);
        updateTotal(-parseFloat(customExpenseInput));
        reAddOption(expenseValue, expenseText); // Add option back to dropdown
    });

    row.appendChild(expenseInfo);
    row.appendChild(deleteBtn);
    expensesList.appendChild(row);

    updateTotal(parseFloat(customExpenseInput));

    document.getElementById('custom-expense').value = "";
    select.value = "";
});

document.getElementById('submit-btn').addEventListener('click', function() {
    var expensesList = document.getElementById('expenses-list');
    var rows = expensesList.getElementsByClassName('row');
    var expenses = {};
    var total = 0;

    for (var i = 0; i < rows.length; i++) {
        var expenseInfo = rows[i].getElementsByTagName('div')[0].textContent;
        var expense = expenseInfo.split(": ")[0];
        var cost = parseFloat(expenseInfo.split(": $")[1]);
        expenses[expense] = cost;
        total += cost;
    }

    var budgetData = {
        "Monthly_Income_After_Tax": expenses["Income After Tax"],
        "Expenses": expenses
    };

    console.log(budgetData)

    fetch("http://127.0.0.1:4444/budget", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(budgetData)
    })
    .then(response => response.json())
    .then(budgetResponse => {
        console.log('Budget response:', budgetResponse);
        let username = getCookie("username");  // Make sure this function is defined or handled properly

        var saveData = {
            "Username": username,
            "Expenses": expenses  // Match the expected structure from your Python API
        };

        return fetch("http://127.0.0.1:4444/save_expenses", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(saveData)
        });
    })
    .then(response => response.json())
    .then(saveResponse => {
        console.log('Save expenses response:', saveResponse);
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
});



function updateTotal(amount) {
    var totalElement = document.getElementById('total');
    var currentTotal = parseFloat(totalElement.textContent.replace('Total: $', ''));
    currentTotal += amount;
    totalElement.textContent = 'Total: $' + currentTotal.toFixed(2);
}

function reAddOption(value, text) {
    var select = document.getElementById('expense-select');
    var optionExists = Array.from(select.options).some(function(option) {
        return option.value === value;
    });
    if (!optionExists) {
        var optionElement = document.createElement('option');
        optionElement.value = value;
        optionElement.textContent = text;
        if (removedOptionIndex !== -1) {
            select.add(optionElement, removedOptionIndex); // Insert option at original index
            removedOptionIndex = -1; // Reset removedOptionIndex
        } else {
            select.appendChild(optionElement); // Append option at the end if no original index is found
        }
    }
}

// Function to remove an option from the dropdown
function removeOption(value) {
    var select = document.getElementById('expense-select');
    for (var i = 0; i < select.options.length; i++) {
        if (select.options[i].value === value) {
            removedOptionIndex = i; // Store the index of the removed option
            select.remove(i);
            break;
        }
    }
}

function getCookie(cname) {
    let name = cname + "=";
    let ca = document.cookie.split(';');
    for(let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
}
