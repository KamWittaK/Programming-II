// Update your JavaScript code
let currentIndex = 0;
const slider = document.querySelector('.slider');
const loadingSpinner = document.querySelector('.loading-spinner');

// Function to make GET request to fetch stock data
async function fetchStockData() {
    try {
        const response = await fetch('http://127.0.0.1:4444/predict_all_stocks');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching stock data:', error);
        return []; // Return an empty array in case of error
    }
}

async function fetchStockChart(symbol) {
    const apiKey = '96IVATSNVA058BJM';
    const apiUrl = `https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=${symbol}&interval=5min&apikey=${apiKey}`;

    try {
        const response = await fetch(apiUrl);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching stock chart data:', error);
        return null;
    }
}

function createStockBox(container, stockData) {
    const box = document.createElement('div');
    box.classList.add('box');

    const ticker = document.createElement('h3');
    ticker.textContent = stockData.Ticker;
    ticker.classList.add('ticker'); // Add the ticker class
    box.appendChild(ticker);

    const chartCanvas = document.createElement('canvas');
    chartCanvas.classList.add('stock-chart');
    box.appendChild(chartCanvas);

    fetchStockChart(stockData.Ticker)
        .then(chartData => {
            if (chartData) {
                renderChart(chartCanvas, chartData);
            } else {
                console.error('Failed to fetch stock chart data.');
            }
        });

    container.appendChild(box);
}


async function renderSlider() {
    // Show loading spinner
    loadingSpinner.style.display = 'block';

    const stockData = await fetchStockData();
    slider.innerHTML = ''; // Clear previous content

    stockData.forEach(stock => {
        createStockBox(slider, stock);
    });

    // Hide loading spinner after fetch is complete
    loadingSpinner.style.display = 'none';
}


function renderChart(canvas, chartData) {
    // Extract the necessary data from the API response
    const timestamps = Object.keys(chartData['Time Series (5min)']); // Assuming Alpha Vantage API format
    const times = timestamps.map(timestamp => timestamp.split(' ')[1]); // Extracting time portion only

    const prices = timestamps.map(timestamp => parseFloat(chartData['Time Series (5min)'][timestamp]['4. close']));

    // Create a new Chart.js chart
    const myChart = new Chart(canvas.getContext('2d'), {
        type: 'line',
        data: {
            labels: times, // Use the extracted times as labels
            datasets: [{
                label: 'Stock Price',
                data: prices // Use the extracted prices as data
            }]
        },
        options: {
            scales: {
                x: {
                    ticks: {
                        maxTicksLimit: 10, // Maximum number of ticks to display
                        stepSize: 3 // Adjust the step size of the ticks as needed
                    }
                }
            }
        }
    });

    return myChart; // Return the created chart instance
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

// Render the slider on page load
renderSlider();
