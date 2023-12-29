const btnShow = document.getElementById('btnShow');
const ordersDivs = document.querySelectorAll('.order');

btnShow.onclick = function() {
    for (var i = 0; i < ordersDivs.length; i++) {
        if (ordersDivs[i].style.display === 'none') {
            ordersDivs[i].style.display = 'block';
        }
    }
}

// Attach click event listeners to each div
ordersDivs.forEach(function(div) {
    div.querySelector('.btnRmv').addEventListener('click', function() {
        // Hide the clicked div
        div.style.display = 'none';
    });
});
