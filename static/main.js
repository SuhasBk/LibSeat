var reservePayload = {}

window.onload = () => {
    const dateElement = document.getElementById("startDate");
    const d = new Date();
    const today = d.toISOString().slice(0, 10);

    const futureDate = new Date();
    futureDate.setDate(futureDate.getDate() + 15);
    const maxDate = futureDate.toISOString().slice(0, 10);

    dateElement.value = today;
    dateElement.setAttribute("min", today);
    dateElement.setAttribute("max", maxDate);
}

document.getElementById('search').addEventListener('click', (e) => {
    e.preventDefault();
    let itemId = document.getElementById('itemId').value;
    let lname = document.getElementById('lname').value;
    let fname = document.getElementById('fname').value;
    let email = document.getElementById('email').value;
    let startDate = document.getElementById('startDate').value;

    if (!itemId || !lname || !fname || !email || !startDate) {
        displayError("All fields are mandatory!");
        return;
    }

    if (!email.includes('mavs.uta.edu')) {
        displayError("Please enter Maverick Email ID!");
        return;
    }

    let data = {
        itemId: itemId,
        fname: fname,
        lname: lname,
        email: email,
        startDate: startDate
    }

    reservePayload['itemId'] = itemId;
    reservePayload['fname'] = fname;
    reservePayload['lname'] = lname;
    reservePayload['email'] = email;
    reservePayload['startDate'] = startDate;

    document.getElementById('search-spinner').removeAttribute('hidden');

    fetch('/api/v1/search', {
        'method': 'POST',
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': JSON.stringify(data)
    })
    .then(res => res.json())
    .then(res => {
        document.getElementById('search-spinner').setAttribute('hidden', 'true');
        let grid = document.getElementById('grid');
        let gridBody = grid;
        gridBody.replaceChildren();
        if (Object.keys(res).includes('slots') && res['slots'].length) {
            document.getElementById('summary').removeAttribute('hidden');
            document.getElementById('summary').innerText = 'Available time slots:';
            document.getElementById('reserve').removeAttribute('hidden');
            let slots = res['slots'];

            let row = document.createElement('tr');

            slots.forEach(slot => {
                let cell = document.createElement('td');
                let checkbox = document.createElement('input');
                let startTime = slot.start.split(' ')[1];
                let endTime = slot.end.split(' ')[1];
                let timeData = `${startTime.slice(0, 5)} to ${endTime.slice(0, 5)}`;
                checkbox.id = 'checkbox-' + slot.checksum;
                checkbox.type = 'checkbox';
                checkbox.value = slot.checksum;
                checkbox.classList.add('available-slots');
                checkbox.setAttribute('timedata', timeData);
                let text = document.createTextNode(timeData);
                
                cell.id = slot.checksum;
                
                checkbox.addEventListener('click', (e) => {
                    let checksum = e.currentTarget.value;
                    let cell = document.getElementById(checksum);
                    if (e.target.checked) {
                        cell.classList.add('checked');
                        cell.style.backgroundColor = 'lightgreen';
                    } else {
                        cell.classList.remove('checked');
                        cell.style.backgroundColor = 'white';
                    }
                });

                cell.addEventListener('click', (e) => {
                    let checksum = e.currentTarget.id;
                    let checkbox = document.getElementById('checkbox-' + checksum);
                    if (e.target.classList.contains('checked')) {
                        checkbox.checked = false;
                        e.target.classList.remove('checked');
                        cell.style.backgroundColor = 'white';
                    } else {
                        checkbox.checked = true;
                        e.target.classList.add('checked');
                        cell.style.backgroundColor = 'lightgreen';
                    }
                });

                cell.appendChild(checkbox);
                cell.appendChild(text);
                row.appendChild(cell);
            });

            gridBody.appendChild(row);
        } else {
            displayError('No slots available on this date!');
        }
    });
});

document.getElementById('reserve').addEventListener('click', (e) => {
    e.preventDefault();
    
    let bookings = [];
    let totalSlots = document.getElementsByClassName('available-slots');

    Array.from(totalSlots).forEach(slot => {
        if (slot.checked) {
            bookings.push({
                checksum: slot.value,
                time: slot.getAttribute('timedata')
            });
        }
    });

    if (bookings.length > 6) {
        displayError('Cannot reserve more than 6 slots per student!');
        return;
    }

    if (bookings.length == 0) {
        displayError('Please select at least one slot!');
        return;
    }

    reservePayload['bookings'] = bookings;

    document.getElementById('reserve-spinner').removeAttribute('hidden');

    fetch('/api/v1/reserve', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(reservePayload)
    })
    .then(res => res.json())
    .then(res => {
        if (res['err']) {
            displayError(res['err']);
        } else {
            displaySuccess(res['msg']);
        }
        document.getElementById('reserve-spinner').setAttribute('hidden', 'true');
    });

});

let displaySuccess = (msg) => {
    let successBanner = document.getElementById('success-banner');
    successBanner.textContent = msg;
    successBanner.removeAttribute('hidden', true);

    setTimeout(() => {
        successBanner.textContent = '';
        successBanner.setAttribute('hidden', true);
    }, 5000);
}

let displayError = (msg) => {
    let failureBanner = document.getElementById('failure-banner');
    failureBanner.textContent = msg;
    failureBanner.removeAttribute('hidden', true);

    setTimeout(() => {
        failureBanner.textContent = '';
        failureBanner.setAttribute('hidden', true);
    }, 5000);
}