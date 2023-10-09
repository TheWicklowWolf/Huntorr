var searchButton = document.getElementById('searchButton');
var searchText = document.getElementById('searchText');
var choiceButton = document.getElementById("choiceButton");
var choiceNo = document.getElementById("choiceNo");
var tableDiv = document.getElementById('tableDiv');
var Radio1377X = document.getElementById('Radio1377X');
var RadioEZTV = document.getElementById('RadioEZTV');
var RadioPB = document.getElementById('RadioPB');
var selectionGroup = document.getElementById('selectionGroup');
var engineText = "";

searchText.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        performSearch();
    }
});

searchButton.addEventListener('click', performSearch);

function performSearch() {
    // Disable Buttons
    searchButton.disabled = true;
    searchText.disabled = true;
    choiceButton.disabled = true;
    choiceNo.disabled = true;
    Radio1377X.disabled = true;
    RadioEZTV.disabled = true;
    RadioPB.disabled = true;
    // Get selected radio button
    if (document.getElementById('Radio1377X').checked) {
        engineText = '1377X';
    }
    else if (document.getElementById('RadioEZTV').checked) {
        engineText = 'EZTV';
    }
    else if (document.getElementById('RadioPB').checked) {
        engineText = 'PB';
    }
    fetch('/search', {
        headers: {
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({ input: searchText.value, engine: engineText })
    })
        .then(function (response) {
            if (response.ok) {
                response.json()
                    .then(function (response) {
                        selectionGroup.style.display = "flex";
                        // Delete exisiting table
                        while (tableDiv.firstChild) {
                            tableDiv.removeChild(tableDiv.firstChild);
                        }
                        // Insert into table
                        tableDiv.insertAdjacentHTML('beforeend', response["table"]);
                        var actualTable = document.getElementsByClassName("dataframe tableStyle");

                        actualTable[0].addEventListener('click', function (e) {
                            var selectedRow = e.target.parentElement.rowIndex - 1;
                            if (selectedRow >= 0 && !isNaN(selectedRow)) {
                                choiceNo.value = selectedRow;
                            }
                        });
                    });
            }
            else {
                throw Error('Something went wrong');
            }
            // Enable Buttons
            searchButton.disabled = false;
            searchText.disabled = false;
            choiceButton.disabled = false;
            choiceNo.disabled = false;
            Radio1377X.disabled = false;
            RadioEZTV.disabled = false;
            RadioPB.disabled = false;
        })
        .catch(function (error) {
            console.log(error);
        });
}

choiceNo.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        performChoice();
    }
});

choiceButton.addEventListener('click', performChoice);


function performChoice() {
    if (choiceNo.value.length == 0 || isNaN(choiceNo.value) || choiceNo.value < 0) {
        alert("Incorrect Entry\nEnter a number to download");
    }
    else {
        choiceButton.disabled = true;
        fetch('/send_magnet', {
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST',
            body: JSON.stringify({ "choice": choiceNo.value })
        })
            .then(function (response) {
                if (response.ok) {
                    response.json()
                        .then(function (response) {
                            choiceButton.disabled = false;
                            choiceNo.style.color = 'blue';
                            choiceNo.value = response.Status;
                            setTimeout(function () {
                                choiceNo.value = "Enter Choice Number";
                                choiceNo.style.color = '';
                            }, 3000);
                        });
                }
                else {
                    throw Error('Something went wrong');
                }
            })
            .catch(function (error) {
                console.log(error);
            });
    }
}
