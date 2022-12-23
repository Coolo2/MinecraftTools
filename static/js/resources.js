
submit = document.getElementById("search-submit")
query = document.getElementById("search-query")
spinner = document.getElementById("spinner")
results = document.getElementById("results")
selected = document.getElementById("selected")


submit.onclick = async function() {
    
    spinner.style.display = "inline-block"

    r = await fetch(`/api/resources/search?q=${encodeURIComponent(query.value)}`)
    j = await r.json()

    results.scrollTo(0, 0);

    results.innerHTML = ""
    for (result of j) {
        e = document.getElementById("example-result").innerHTML 
        e = e.replace("{name}", result.name)
        e = e.replace("{description}", result.description)

        if (result.icon_url) {
            e = e.replace("{icon}", result.icon_url)
        } else {
            e = e.replace("{icon}", `/static/images/${result.site}.png`)
        }
        
        e = e.split("{self_id}").join(result.self_id)
        e = e.split("{site}").join(result.site)
        results.innerHTML += e

        
    }

    spinner.style.display = "none"
    selected.style.display = "none"
}

document.onclick = async function(e) {
    if (e.target.id.includes("result-")) {
        for (result of j) {
            if (result.self_id == e.target.id.replace("result-", "")) {
                spinner.style.display = "inline-block"

                r = await fetch(`/api/resources/extra/${result.self_id}`)
                result = await r.json()
    
                document.getElementById(e.target.id).classList.add("result-selected")
                document.getElementById("selected-name").innerText = result.name
                document.getElementById("selected-description").innerText = result.description 
                
                document.getElementById("selected-site").src = `/static/images/${result.site}.png`
                document.getElementById("selected-download").href = `/resources/download/${result.self_id}`
                document.getElementById("selected-view").href = result.url
                document.getElementById("selected-view").innerText = `View on ${result.site}`
                document.getElementById("selected-site-balloon").setAttribute("aria-label", `This is a plugin from the ${result.site} website`)
                document.getElementById("selected-api").innerText = result.api
                document.getElementById("selected-downloads").innerText = numberWithCommas(result.downloads)

                if (result.icon_url) {document.getElementById("selected-icon").src = result.icon_url
                } else {document.getElementById("selected-icon").src = `/static/images/${result.site}.png`} 

                if (result.download_type == "external") {document.getElementById("selected-download").innerText = "Download (external)"
                } else {document.getElementById("selected-download").innerText = "Download"}

                selected.style.display = "block"
                spinner.style.display = "none"

            } else {
                document.getElementById(`result-${result.self_id}`).classList.remove("result-selected")
            }
        }
    }
}

document.onkeydown = async function (k) {
    
    if (k.path && k.path[0] && k.path[0].id == query.id && k.key == "Enter") {
        submit.click()
    }
}