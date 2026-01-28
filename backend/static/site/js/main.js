document.addEventListener('DOMContentLoaded', () => {
  // Discount timer
  const timerEl = document.getElementById('discount-timer');
  if (timerEl) {
    const deadlineStr = timerEl.dataset.deadline;
    const deadline = new Date(deadlineStr);
    const tick = () => {
      const now = new Date();
      let diff = Math.max(0, deadline.getTime() - now.getTime());
      const sec = Math.floor(diff / 1000) % 60;
      const min = Math.floor(diff / (1000 * 60)) % 60;
      const hr = Math.floor(diff / (1000 * 60 * 60)) % 24;
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      timerEl.textContent = `${String(days).padStart(2, '0')}д : ${String(hr).padStart(2, '0')}ч : ${String(min).padStart(2, '0')}м`;
    };
    tick();
    setInterval(tick, 60000);
  }

  // Reviews accordion
  document.querySelectorAll('.review-header').forEach((btn) => {
    btn.addEventListener('click', () => {
      const card = btn.closest('.review-card');
      const isOpen = card.classList.contains('open');
      document.querySelectorAll('.review-card').forEach((c) => c.classList.remove('open'));
      if (!isOpen) {
        card.classList.add('open');
      }
    });
  });

  // Time calculator
  const progressFill = document.getElementById('timecalc-progress-fill');
  const steps = document.querySelectorAll('.timecalc-step');
  const progressSteps = document.querySelectorAll('.timecalc-progress-steps span');
  const optionsBlocks = document.querySelectorAll('.timecalc-options');
  const taskList = document.getElementById('timecalc-task-list');
  const totalAnimatedEl = document.getElementById('timecalc-total-animated');
  const totalFinalEl = document.getElementById('timecalc-total-final');
  const resultTextEl = document.getElementById('timecalc-result-text');

  let currentStep = 1;
  let totalHoursBase = 195;
  let totalHoursCurrent = totalHoursBase;

  const setStep = (step) => {
    currentStep = step;
    steps.forEach((el) => {
      el.classList.toggle('active', Number(el.dataset.step) === step);
    });
    progressSteps.forEach((span, index) => {
      span.classList.toggle('active', index === step - 1);
    });
    if (progressFill) {
      progressFill.style.width = `${step * 33.33}%`;
    }
  };

  const updateResultText = () => {
    const hours = totalHoursCurrent;
    const days = Math.round((hours / 24) * 10) / 10;
    if (resultTextEl) {
      resultTextEl.textContent =
        `${hours} часов — это примерно ${days} суток. Столько времени вы потратите не на сам ремонт, ` +
        `а на организацию. С «БригАдрес» эти часы вы проведёте с семьёй, в путешествиях и за любимыми делами, ` +
        `а мы возьмём организацию на себя.`;
    }
  };

  if (optionsBlocks.length) {
    optionsBlocks.forEach((block) => {
      block.addEventListener('click', (e) => {
        const btn = e.target.closest('.timecalc-option');
        if (!btn) return;
        block.querySelectorAll('.timecalc-option').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });
  }

  if (taskList && totalAnimatedEl) {
    const items = taskList.querySelectorAll('li');
    let selectedHours = 0;

    const recalc = () => {
      totalHoursBase = Array.from(items).reduce((sum, li) => sum + Number(li.dataset.hours || 0), 0);
      totalHoursCurrent = selectedHours || totalHoursBase;
      totalAnimatedEl.textContent = `${totalHoursCurrent} часов`;
      if (totalFinalEl) totalFinalEl.textContent = `~${totalHoursCurrent} часов`;
      updateResultText();
    };

    items.forEach((li) => {
      li.addEventListener('click', () => {
        li.classList.toggle('active');
        selectedHours = Array.from(items)
          .filter((x) => x.classList.contains('active'))
          .reduce((sum, el) => sum + Number(el.dataset.hours || 0), 0);
        recalc();
      });
    });

    recalc();
  }

  const startBtn = document.getElementById('timecalc-start');
  const toResultBtn = document.getElementById('timecalc-to-result');

  if (startBtn) {
    startBtn.addEventListener('click', () => {
      const typeBtn = document.querySelector('.timecalc-options[data-name="type"] .timecalc-option.active');
      const materialsBtn = document.querySelector('.timecalc-options[data-name="materials"] .timecalc-option.active');

      let typeCoef = 1;
      let matCoef = 1;

      if (typeBtn) {
        if (typeBtn.dataset.value === 'cosmetic') typeCoef = 0.7;
        if (typeBtn.dataset.value === 'capital') typeCoef = 1;
        if (typeBtn.dataset.value === 'full') typeCoef = 1.1;
      }
      if (materialsBtn) {
        if (materialsBtn.dataset.value === 'yes') matCoef = 1.1;
        if (materialsBtn.dataset.value === 'no') matCoef = 1;
      }
      totalHoursCurrent = Math.round(195 * typeCoef * matCoef);
      if (totalAnimatedEl) totalAnimatedEl.textContent = `${totalHoursCurrent} часов`;
      if (totalFinalEl) totalFinalEl.textContent = `~${totalHoursCurrent} часов`;
      updateResultText();
      setStep(2);
    });
  }

  if (toResultBtn) {
    toResultBtn.addEventListener('click', () => {
      setStep(3);
    });
  }

  setStep(1);

  
  // Document slider on странице с документами
  const docSlider = document.querySelector('.doc-slider');
  if (docSlider) {
    const track = docSlider.querySelector('.doc-slider-track');
    const slides = docSlider.querySelectorAll('.doc-slide');
    const dots = docSlider.querySelectorAll('.doc-slider-dot');
    const prev = docSlider.querySelector('.doc-slider-prev');
    const next = docSlider.querySelector('.doc-slider-next');
    let current = 0;

    const total = slides.length;
    if (!track || !total) return;

    // Make slide widths deterministic so соседние слайды не выглядывали по краям
    const step = 100 / total;
    track.style.width = `${total * 100}%`;
    slides.forEach((slide) => {
      slide.style.flex = `0 0 ${step}%`;
      slide.style.maxWidth = `${step}%`;
    });

    const goTo = (index) => {
      current = (index + total) % total;
      track.style.transform = `translate3d(-${current * step}%, 0, 0)`;
      dots.forEach((dot, idx) => {
        dot.classList.toggle('active', idx === current);
      });
    };

    if (prev) prev.addEventListener('click', () => goTo(current - 1));
    if (next) next.addEventListener('click', () => goTo(current + 1));
    dots.forEach((dot, idx) => {
      dot.addEventListener('click', () => goTo(idx));
    });

    goTo(0);
  }

// Dummy submit handler for form
  document.querySelectorAll('.lead-form').forEach((form) => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const success = form.querySelector('.form-success');
      if (success) {
        success.hidden = false;
      }
    });
  });
});
