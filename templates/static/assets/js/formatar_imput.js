document.addEventListener('DOMContentLoaded', (event) => {
    function formatField(inputElement, format) {
        if (inputElement !== null) {
            inputElement.addEventListener('input', function () {
                let value = this.value.replace(/\D/g, '') // Remove todos os caracteres não numéricos
                let formattedValue = ''

                for (let i = 0; i < format.length && value.length > 0; i++) {
                    if (format[i] === '#') {
                        formattedValue += value[0]
                        value = value.slice(1)
                    } else {
                        formattedValue += format[i]
                    }
                }

                this.value = formattedValue
            })
        }
    }

    // Usando a função formatField para formatar o campo "cep"
    formatField(document.getElementById('cep'), '#####-####')

    // Usando a função formatField para formatar o campo "id_cep"
    formatField(document.querySelector('#id_cep'), '#####-####')

    // Usando a função formatField para formatar o campo "id_telefone"
    formatField(document.querySelector('#id_telefone'), '(##) #####-####')
})
