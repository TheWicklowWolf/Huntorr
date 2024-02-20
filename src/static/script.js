var config_modal = document.getElementById('config-modal');
var save_message = document.getElementById("save-message");
var save_changes_button = document.getElementById("save-changes-button");
var sync_message = document.getElementById("sync-message");
var sync_button = document.getElementById("sync-button");
var searchButton = document.getElementById('searchButton');
var searchText = document.getElementById('searchText');
var choiceButton = document.getElementById("choiceButton");
var choiceNo = document.getElementById("choiceNo");
var tableDiv = document.getElementById('tableDiv');
var Radio1337X = document.getElementById('Radio1337X');
var RadioEZTV = document.getElementById('RadioEZTV');
var RadioPB = document.getElementById('RadioPB');
var selectionGroup = document.getElementById('selectionGroup');
var media_server_addresses = document.getElementById("media_server_addresses");
var media_server_tokens = document.getElementById("media_server_tokens");
var media_server_library_name = document.getElementById("media_server_library_name");
var engineText = "PB";
var timer = null;

searchText.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        performSearch();
    }
});

searchButton.addEventListener('click', performSearch);

function performSearch() {
    searchButton.disabled = true;
    searchText.disabled = true;
    choiceButton.disabled = true;
    choiceNo.disabled = true;
    Radio1337X.disabled = true;
    RadioEZTV.disabled = true;
    RadioPB.disabled = true;
    if (Radio1337X.checked) {
        engineText = '1337X';
    }
    else if (RadioEZTV.checked) {
        engineText = 'EZTV';
    }
    else if (RadioPB.checked) {
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
                                if (timer) {
                                    clearTimeout(timer);
                                    choiceNo.style.color = '';
                                    timer = null;
                                }
                            }
                        });
                    });
            }
            else {
                throw Error('Something went wrong');
            }
            searchButton.disabled = false;
            searchText.disabled = false;
            choiceButton.disabled = false;
            choiceNo.disabled = false;
            Radio1337X.disabled = false;
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
                            timer = setTimeout(function () {
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

config_modal.addEventListener('show.bs.modal', function (event) {
    fetch('/load_settings', {
        headers: {
            'Content-Type': 'application/json'
        },
        method: 'GET'
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            media_server_addresses.value = data.media_server_addresses;
            media_server_tokens.value = data.media_server_tokens;
            media_server_library_name.value = data.media_server_library_name;
        })
        .catch(error => {
            console.error('Fetch error:', error);
        });
});

save_changes_button.addEventListener("click", () => {
    fetch('/save_settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "media_server_addresses": media_server_addresses.value,
            "media_server_tokens": media_server_tokens.value,
            "media_server_library_name": media_server_library_name.value,
        }),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            save_message.style.display = "block";
            setTimeout(function () {
                save_message.style.display = "none";
            }, 1500);
        })
        .catch(error => {
            console.error('Fetch error:', error);
        });
});

sync_button.addEventListener("click", () => {
    fetch('/refresh_media_server', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            sync_message.style.display = "block";
            sync_message.textContent = data.Status;
            setTimeout(function () {
                sync_message.style.display = "none";
            }, 3000);
        })
        .catch(error => {
            console.error('Fetch error:', error);
        });
});

const themeSwitch = document.getElementById('themeSwitch');
const savedTheme = localStorage.getItem('theme');
const savedSwitchPosition = localStorage.getItem('switchPosition');

if (savedSwitchPosition) {
    themeSwitch.checked = savedSwitchPosition === 'true';
}

if (savedTheme) {
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
}

themeSwitch.addEventListener('click', () => {
    if (document.documentElement.getAttribute('data-bs-theme') === 'dark') {
        document.documentElement.setAttribute('data-bs-theme', 'light');
    } else {
        document.documentElement.setAttribute('data-bs-theme', 'dark');
    }
    localStorage.setItem('theme', document.documentElement.getAttribute('data-bs-theme'));
    localStorage.setItem('switchPosition', themeSwitch.checked);
});
