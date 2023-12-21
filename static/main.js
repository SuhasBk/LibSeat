window.onload = function() {
    const d = new Date();
    const today = d.toISOString().slice(0, 10);
    const currTime = d.toLocaleTimeString(undefined, { 'hour12': false }).slice(0, 5);

    const futureDate = new Date();
    futureDate.setDate(futureDate.getDate() + 15);
    const maxDate = futureDate.toISOString().slice(0, 10);

    document.getElementById("dateTime").setAttribute("min", today + "T" + currTime);
    document.getElementById("dateTime").setAttribute("max", maxDate + "T21:00");
}

document.getElementById("dateTime").addEventListener("change", function () {
    const now = new Date();
    const selectedTime = new Date(this.value);
    const startDate = selectedTime.getFullYear() + '-' + (selectedTime.getMonth() + 1) + '-' + selectedTime.getDate();

    const hours = selectedTime.getHours();
    const minutes = selectedTime.getMinutes();

    if (hours < 9 || hours > 23 || minutes%30 != 0 || (selectedTime.getDate() == now.getDate() && (hours < now.getHours() || (hours == now.getHours() && minutes <= now.getMinutes())))) {
        alert("Please select a future time between 9 AM and 11 PM with 30 minute interval only.");
        this.value = "";
        return;
    }    
});