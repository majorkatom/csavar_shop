var sumVATnotIncluded = document.getElementById("sumVATnotIncluded");
var vat = document.getElementById("VAT");
var sumVATincluded = document.getElementById("sumVATincluded");
var boltRows = Array.from(document.getElementById("cart_table").getElementsByTagName("tr")).slice(1);

function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(";");
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        c = c.trim();
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

// összesített árak számítása és html-be írása
function calculateSum(){
    var noVAT = 0;
    boltRows.forEach(element => {
        rowPriceText = element.getElementsByClassName("price_per_bolt")[0].innerHTML;
        noVAT += parseInt(rowPriceText);
    });
    sumVATnotIncluded.innerHTML = String(noVAT) + " Ft";
    vat.innerHTML = String(Math.ceil(noVAT * 0.27)) + " Ft";
    sumVATincluded.innerHTML = String(parseInt(sumVATnotIncluded.innerHTML) + parseInt(vat.innerHTML)) + " Ft";
}

calculateSum();

// a táblázat minden sorára
boltRows.forEach(element => {
    // ha változtatjuk a mennyiséget, akkor írja felöl a kosár sütiben az adatokat
    element.getElementsByClassName("qty")[0].addEventListener("change", (e) => {
        var priceEAtext = element.getElementsByClassName("priceEA")[0].innerHTML
        var priceEA = parseInt(priceEAtext.slice(priceEAtext.indexOf(" ")));
        var qty = parseInt(e.target.value);
        element.getElementsByClassName("price_per_bolt")[0].innerHTML = String(priceEA * qty) + " Ft";
        calculateSum()
        var cookieObj = JSON.parse(getCookie("cart"));
        var idText = element.id;
        cookieObj[idText.slice(0, idText.indexOf("bolt_id"))] = qty;
        var time = new Date();
        var expiry = new Date(time.getTime() + 1 * 24 * 3600 * 1000);
        document.cookie = "cart=" + JSON.stringify(cookieObj) + ";expires=" + expiry.toUTCString() + ";path=/;Secure;";
    })

    // az eltávolítás gombra a csavar törlése a sütiből és a kosár oldal újratöltése
    element.getElementsByTagName("button")[0].addEventListener("click", () => {
        var cookieObj = JSON.parse(getCookie("cart"));
        var idText = element.id
        delete cookieObj[idText.slice(0, idText.indexOf("bolt_id"))];
        var time = new Date();
        var expiry = new Date(time.getTime() + 1 * 24 * 3600 * 1000);
        document.cookie = "cart=" + JSON.stringify(cookieObj) + ";expires=" + expiry.toUTCString() + ";path=/;Secure;";
        window.location = "/kosar";
    })
});