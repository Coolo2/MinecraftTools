function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

window.onscroll = async function() {
    //document.body.style.backgroundPositionY = `${window.scrollY/3}px`
}