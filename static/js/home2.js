// let dias_mes = {
//     'janeiro'   : [1 , 31] ,
//     'fevereiro' : [1 , 28] ,
//     'março'     : [1 , 31] ,
//     'abril'     : [1 , 30] ,
//     'maio'      : [1 , 31] ,
//     'junho'     : [1 , 30] ,
//     'julho'     : [1 , 31] ,
//     'agosto'    : [1 , 31] ,
//     'setembro'  : [1 , 30] ,
//     'outubro'   : [1 , 31] ,
//     'novembro'  : [1 , 30] ,
//     'dezembro'  : [1 , 31] ,
// }

function enviar(txt){
    console.log(txt)
}

let dias_mes = [
    [31] ,
    [28] ,
    [31] ,
    [30] ,
    [31] ,
    [30] ,
    [31] ,
    [31] ,
    [30] ,
    [31] ,
    [30] ,
    [31] ,
]
let meses = [
    'janeiro',
    'fevereiro',
    'março',
    'abril',
    'maio',
    'junho',
    'julho',
    'agosto',
    'setembro',
    'outubro',
    'novembro',
    'dezembro',
]

let data = new Date()
let anov = data.getFullYear()
let mesv = data.getMonth()
let diav = data.getDate()

console.log(diav)


let range = dias_mes[mesv]
for(let i = diav;i<=range;i++){
    let calendario = document.getElementsByClassName('calendar-grid')
    // let nome       = document.getElementById('')

    let celula     = document.createElement('div')
    celula.classList.add('day-cell')
    // celula.classList.add('conf')

    let dia        = document.createElement('span')
    dia.classList.add('day-number')
    celula.addEventListener('click' , ()=>{enviar(dia.textContent)})

    // console.log(dia)
    dia.innerText  = `${i}`

    // console.log(celula)
    celula.appendChild(dia)
    calendario[0].appendChild(celula)

}

document.addEventListener('DOMContentLoaded', () => {
    const newAppointmentBtn = document.querySelector('.new-appointment-btn');
    const form = document.querySelector('.Form');

    newAppointmentBtn.addEventListener('click', () => {
      form.classList.toggle('hidden');
    });
  });

// console.log(calendario.item(0))
function openAppointmentForm(day) {
  const appointmentForm = document.getElementById("appointmentForm");
  const dateInput = document.getElementById("date");
  const monthNames = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
  ];

  if (day) {
    dateInput.value = `${day} de ${monthNames[currentMonth]} de ${currentYear}`;
  } else {
    dateInput.value = "Escolha um dia no calendário.";
  }

  appointmentForm.classList.remove("hidden");
}

