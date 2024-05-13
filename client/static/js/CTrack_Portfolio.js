let currentIndex = 0;
const slider = document.querySelector('.slider');

function GetResults() {
    return new Promise((resolve, reject) => {
        let username = getCookie("username");
        let saveData = {
            Username: username
        };
        fetch("http://127.0.0.1:4444/get_expenses", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(saveData)
        })
        .then(response => response.json())
        .then(data => {
            let budgetData = {
                Monthly_Income_After_Tax: data.Data.Monthly_Income_After_Tax,
                Expenses: data.Data.Expenses
            };
        
            fetch("http://127.0.0.1:4444/budget", {
                method: "POST",       
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(budgetData)
            })
            .then(response => response.json())
            .then(budgetResponse => {
                console.log(budgetResponse); // Prints the response from the budget endpoint
                resolve(budgetResponse); // Resolve the promise with budgetResponse
            })
            .catch(error => reject(error));
        })
        .catch(error => reject(error));
    });
}

async function renderSlider() {
    const slider = document.getElementById('slider');

    try {
        const data = await GetResults();
        console.log(GetResults)

        if (data && data.result) {
            const results = data.result;

            for (const [expense, status] of Object.entries(results)) {
                createBox(slider, `${expense}: ${status}`);
            }
        } else {
            console.error('No result data found.');
        }
    } catch (error) {
        // Handle error
        console.error('There was a problem rendering the slider:', error);
    }
}

function createBox(container, content) {
    const box = document.createElement('div');
    box.classList.add('box');

    const title = document.createElement('h3');
    title.textContent = content;
    box.appendChild(title);

    container.appendChild(box);
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

// Function to handle navigation to the previous slide
function prevSlide() {
    if (currentIndex > 0) {
        currentIndex--;
        slider.style.transform = `translateX(-${currentIndex * 100}%)`;
    }
}

// Function to handle navigation to the next slide
function nextSlide() {
    const containerWidth = slider.offsetWidth; // Get width of container
    const visibleCards = Math.floor(containerWidth / 800); // Calculate number of visible cards
    const nextIndex = currentIndex + 1;
    const maxIndex = Math.ceil((slider.childElementCount - visibleCards) / visibleCards);

    if (nextIndex <= maxIndex) {
        currentIndex = nextIndex;
        slider.style.transform = `translateX(-${currentIndex * containerWidth}px)`;
    }
}


renderSlider();
