document.addEventListener("DOMContentLoaded", function () {
    const addBtn = document.getElementById('addBtn');
    const tbody = document.querySelector("tbody");
    const form = document.querySelector("form");

    addBtn.addEventListener("click", function (e) {
        e.preventDefault();

        const product = document.querySelector(".product").value;
        const quantity = document.querySelector(".quantity").value;
    
        tbody.innerHTML += `
            <tr>
                <td>${product}</td>
                <td>${quantity}</td>
                <td><button class="deleteBtn">Remover</button></td>
            </tr>
        `;

    });

    tbody.addEventListener("click", function (e) {
        if (e.target.classList.contains("deleteBtn")) {
            const row = e.target.closest("tr");
            if (row) {
                row.remove();
            }
        }
    });

    form.addEventListener("submit", function (e) {

        const productList = getList(); // Call the function to get the product list

        // Now, you can fetch the data
        sendData(productList);
    });

    const table = document.querySelector('table');

    function getList() {
        var customer = document.getElementsByClassName("customer")[0];
        const ready = document.getElementsByClassName("ready")[0];
        const delivery = document.getElementsByClassName("delivery")[0];
        const notes = document.getElementsByClassName("notes")[0];
        var list = [];
        for (var i = 1; i < table.rows.length; i++) {
            var productCell = table.rows[i].cells[0];
            var quantityCell = table.rows[i].cells[1];
        
            //console.log("Product Cell Text Content:", productCell.textContent);
            //console.log("Quantity Cell Text Content:", quantityCell.textContent);
        
            var produto = {
                product: productCell.innerHTML,
                quantity: quantityCell.innerHTML
            };
        
            list.push(produto);
        }

        var infos = {customer: customer.value , ready: ready.value, delivery: delivery.value, notes: notes.value, produtos: list}
        console.log(infos);
        return infos;
    }

    function sendData(productList) {
        const list_json = JSON.stringify(productList);

        fetch('/orderinfo', {
            //mode: 'cors',
            method: 'POST',
            body: list_json,
            headers: {
                "Content-Type": "application/json"
            }
        })
        .then(response => {
            if (!response.ok) {                                  
                throw new Error("HTTP error " + response.status);  
            }                                                   
            return response.json(); // Parse the JSON in the response
        })
        .then(data => {
            // Use the data returned by the server
            console.log("Server response:", data);
            // ... do something with the data
        })
        .catch(error => {
            // Handle/report error
            console.error("Error:", error);
        });
    }
});

