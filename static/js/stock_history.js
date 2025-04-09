fetch("/log.txt")

            .then(response => response.text())
            .then(data => {
                const lines = data.split('\n');
                const container = document.getElementById('log-container');
                lines.forEach(line => {
                    if (line.trim() !== "") {
                        const div = document.createElement('div');
                        div.textContent = line;
                        div.classList.add('log-line');
                        container.appendChild(div);
                    }
                });
            })
            .catch(error => {
                console.error('Error loading log.txt:', error);
            });