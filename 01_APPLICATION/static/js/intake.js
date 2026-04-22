/**
 * Child Support Intake — Form Wizard JavaScript
 * Handles multi-step navigation, validation, conditional fields,
 * review generation, and form submission.
 */

let currentStep = 1;
const totalSteps = 11;

// ── Initialization ──────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    initYesNoButtons();
    initConditionalLogic();
    initWorksheetCalculation();
    initInputFormatters();
    updateProgress();
});

// ── Auto-Format Inputs (DOB, Phone, SSN) ────────────────────

/**
 * Format a date string as the user types.
 * Accepts: 12151993, 12/15/1993, 12-15-1993
 * Outputs: 12/15/1993
 */
function formatDate(value) {
    // Strip everything except digits
    const digits = value.replace(/\D/g, '').slice(0, 8);
    if (digits.length === 0) return '';
    if (digits.length <= 2) return digits;
    if (digits.length <= 4) return `${digits.slice(0, 2)}/${digits.slice(2)}`;
    return `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4)}`;
}

/**
 * Format a phone number as the user types.
 * Accepts: 9285551234, 928-555-1234, (928) 555-1234
 * Outputs: 928-555-1234
 */
function formatPhone(value) {
    const digits = value.replace(/\D/g, '').slice(0, 10);
    if (digits.length === 0) return '';
    if (digits.length <= 3) return digits;
    if (digits.length <= 6) return `${digits.slice(0, 3)}-${digits.slice(3)}`;
    return `${digits.slice(0, 3)}-${digits.slice(3, 6)}-${digits.slice(6)}`;
}

/**
 * Format a social security number as the user types.
 * Accepts: 123456789, 123-45-6789
 * Outputs: 123-45-6789
 */
function formatSSN(value) {
    const digits = value.replace(/\D/g, '').slice(0, 9);
    if (digits.length === 0) return '';
    if (digits.length <= 3) return digits;
    if (digits.length <= 5) return `${digits.slice(0, 3)}-${digits.slice(3)}`;
    return `${digits.slice(0, 3)}-${digits.slice(3, 5)}-${digits.slice(5)}`;
}

/**
 * Wire up auto-formatting on all inputs with matching names.
 * Uses the input event so formatting happens as the user types.
 */
function initInputFormatters() {
    // Date fields — any input with data-validate="date" or name ending in _dob
    const dateFields = document.querySelectorAll(
        'input[data-validate="date"], input[name$="_dob"], input[name$="_from"], input[name="start_date"]'
    );
    dateFields.forEach(el => {
        el.setAttribute('maxlength', '10');
        el.addEventListener('input', function (e) {
            const caretAtEnd = this.selectionStart === this.value.length;
            const formatted = formatDate(this.value);
            this.value = formatted;
            if (caretAtEnd) {
                this.setSelectionRange(formatted.length, formatted.length);
            }
        });
    });

    // Phone fields
    const phoneFields = document.querySelectorAll('input[type="tel"], input[name$="_phone"]');
    phoneFields.forEach(el => {
        el.setAttribute('maxlength', '12');
        el.addEventListener('input', function (e) {
            const caretAtEnd = this.selectionStart === this.value.length;
            const formatted = formatPhone(this.value);
            this.value = formatted;
            if (caretAtEnd) {
                this.setSelectionRange(formatted.length, formatted.length);
            }
        });
    });

    // SSN fields
    const ssnFields = document.querySelectorAll('input[name$="_ssn"]');
    ssnFields.forEach(el => {
        el.setAttribute('maxlength', '11');
        el.addEventListener('input', function (e) {
            const caretAtEnd = this.selectionStart === this.value.length;
            const formatted = formatSSN(this.value);
            this.value = formatted;
            if (caretAtEnd) {
                this.setSelectionRange(formatted.length, formatted.length);
            }
        });
    });
}

// ── Step Navigation ─────────────────────────────────────────

function nextStep() {
    if (!validateStep(currentStep)) return;

    if (currentStep < totalSteps) {
        document.getElementById(`step${currentStep}`).classList.add('hidden');
        currentStep++;
        document.getElementById(`step${currentStep}`).classList.remove('hidden');
        updateProgress();
        window.scrollTo({ top: 0, behavior: 'smooth' });

        // Run initial worksheet calculation when entering step 9
        if (currentStep === 9) {
            prepopulateWorksheetIncome();
            calcParentingTime();
            calculateWorksheet();
        }

        if (currentStep === totalSteps) {
            buildReview();
        }
    }
}

function prevStep() {
    if (currentStep > 1) {
        document.getElementById(`step${currentStep}`).classList.add('hidden');
        currentStep--;
        document.getElementById(`step${currentStep}`).classList.remove('hidden');
        updateProgress();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function goToStep(step) {
    // Only allow going to completed steps or the current step
    if (step > currentStep) return;
    document.getElementById(`step${currentStep}`).classList.add('hidden');
    currentStep = step;
    document.getElementById(`step${currentStep}`).classList.remove('hidden');
    updateProgress();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function updateProgress() {
    // Update step indicator badge
    document.getElementById('stepIndicator').textContent = `Step ${currentStep} of ${totalSteps}`;

    // Update progress bar fill
    const pct = ((currentStep - 1) / (totalSteps - 1)) * 100;
    document.getElementById('progressFill').style.width = pct + '%';

    // Update step dots
    document.querySelectorAll('.step-dot').forEach(dot => {
        const step = parseInt(dot.dataset.step);
        dot.classList.remove('active', 'completed');
        if (step === currentStep) {
            dot.classList.add('active');
        } else if (step < currentStep) {
            dot.classList.add('completed');
            dot.innerHTML = '&#10003;';
        } else {
            dot.textContent = step;
        }
    });

    // Update labels
    document.querySelectorAll('.step-label').forEach((label, i) => {
        label.classList.toggle('active', i + 1 === currentStep);
    });
}

// ── Yes/No Button Logic ─────────────────────────────────────

function initYesNoButtons() {
    document.querySelectorAll('.yes-no-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const field = this.dataset.field;
            const value = this.dataset.value;
            const group = this.closest('.yes-no-group');
            const hiddenInput = group.parentElement.querySelector(`input[name="${field}"]`);

            // Update button states
            group.querySelectorAll('.yes-no-btn').forEach(b => {
                b.classList.remove('selected-yes', 'selected-no');
            });

            if (value === 'yes') {
                this.classList.add('selected-yes');
            } else {
                this.classList.add('selected-no');
            }

            // Update hidden input
            if (hiddenInput) {
                hiddenInput.value = value;
            }

            // Trigger conditional logic
            handleConditional(field, value);
        });
    });
}

// ── Conditional Sections ────────────────────────────────────

function initConditionalLogic() {
    // Set initial states based on default values
    handleConditional('pet_has_attorney', 'no');
    handleConditional('were_married', 'no');
    handleConditional('requesting_arrears', 'no');
    handleConditional('resp_employed', 'yes');
    handleConditional('pet_employed', 'yes');
    handleConditional('know_resp_income', 'no');
    handleConditional('know_pet_income', 'no');
    handleConditional('request_tax_exemption', 'no');
    handleConditional('address_protection', 'no');
    handleConditional('has_start_date', 'no');
    handleConditional('travel_same_split', 'yes');
}

function handleConditional(field, value) {
    const map = {
        'pet_has_attorney': { section: 'attorney-section', showOn: 'yes' },
        'were_married': { section: 'still-married-section', showOn: 'yes' },
        'requesting_arrears': { section: 'arrears-section', showOn: 'yes' },
        'resp_employed': {
            section: 'resp-employed-section', showOn: 'yes',
            altSection: 'resp-unemployed-section', altShowOn: 'no'
        },
        'pet_employed': { section: 'pet-employed-section', showOn: 'yes' },
        'know_resp_income': { section: 'resp-income-section', showOn: 'yes' },
        'know_pet_income': { section: 'pet-income-section', showOn: 'yes' },
        'request_tax_exemption': { section: 'tax-exemption-section', showOn: 'yes' },
        'address_protection': { section: 'address-protection-section', showOn: 'yes' },
        'has_start_date': {
            section: 'start-date-section', showOn: 'yes',
            altSection: 'court-sets-date', altShowOn: 'no'
        },
        'travel_same_split': { section: 'travel-split-section', showOn: 'no' },
    };

    const config = map[field];
    if (!config) return;

    const el = document.getElementById(config.section);
    if (el) {
        if (value === config.showOn) {
            el.classList.add('visible');
        } else {
            el.classList.remove('visible');
        }
    }

    if (config.altSection) {
        const altEl = document.getElementById(config.altSection);
        if (altEl) {
            if (value === config.altShowOn) {
                altEl.classList.add('visible');
            } else {
                altEl.classList.remove('visible');
            }
        }
    }
}

// ── Child Address Logic ─────────────────────────────────────

function updateChildAddress() {
    const livesWithVal = document.querySelector('input[name="child_lives_with"]:checked').value;
    const addressSection = document.getElementById('child-address-section');
    const autoNote = document.getElementById('child-address-auto');

    if (livesWithVal === 'other') {
        addressSection.classList.add('visible');
        autoNote.style.display = 'none';
    } else {
        addressSection.classList.remove('visible');
        const label = livesWithVal === 'pet' ? "petitioner's" : "respondent's";
        autoNote.textContent = `The child's address will be set to the ${label} address automatically.`;
        autoNote.style.display = 'block';
    }
}

// ── Auto-Calculate Medical Split ────────────────────────────

function autoCalcResp() {
    const petPct = parseFloat(document.querySelector('[name="pet_medical_pct"]').value);
    if (!isNaN(petPct) && petPct >= 0 && petPct <= 100) {
        document.querySelector('[name="resp_medical_pct"]').value = Math.round((100 - petPct) * 10) / 10;
    }
}

// ── Auto-Calculate Worksheet Mother % ────────────────────────

function autoCalcMotherPct() {
    const fatherPct = parseFloat(document.querySelector('[name="ws_father_pct"]').value);
    if (!isNaN(fatherPct) && fatherPct >= 0 && fatherPct <= 100) {
        document.querySelector('[name="ws_mother_pct"]').value = Math.round((100 - fatherPct) * 10) / 10;
    }
}

// ── Arizona Child Support Schedule (2022 Revision) ──────────
//
// Source: Arizona Supreme Court Child Support Guidelines,
// Appendix A — Schedule of Basic Support Obligations
// (effective January 1, 2022, revised January 1, 2023)
//
// This table gives the BASIC CHILD SUPPORT OBLIGATION for the
// given Combined Adjusted Gross Income and number of children.
// Values are sampled at representative income levels and
// linearly interpolated between rows for other incomes.
//
// Format: [combined_adjusted_gross_monthly, [1_child, 2_children, 3_children, 4_children, 5_children, 6_children]]

const AZ_CS_SCHEDULE = [
    [  950, [ 218,  284,  334,  374,  412,  446]],
    [ 1000, [ 226,  295,  347,  388,  427,  463]],
    [ 1100, [ 243,  316,  372,  416,  458,  496]],
    [ 1200, [ 259,  338,  397,  444,  488,  529]],
    [ 1300, [ 275,  359,  422,  472,  519,  562]],
    [ 1400, [ 291,  380,  446,  499,  549,  594]],
    [ 1500, [ 306,  400,  470,  525,  578,  626]],
    [ 1600, [ 322,  420,  493,  551,  607,  657]],
    [ 1700, [ 337,  439,  516,  577,  634,  687]],
    [ 1800, [ 351,  458,  538,  601,  662,  717]],
    [ 1900, [ 365,  477,  560,  626,  688,  746]],
    [ 2000, [ 380,  495,  582,  650,  715,  774]],
    [ 2100, [ 394,  513,  603,  674,  741,  802]],
    [ 2200, [ 407,  531,  624,  697,  766,  830]],
    [ 2300, [ 421,  549,  645,  720,  792,  857]],
    [ 2400, [ 434,  566,  665,  743,  817,  885]],
    [ 2500, [ 447,  583,  685,  765,  841,  911]],
    [ 2600, [ 460,  600,  705,  787,  866,  938]],
    [ 2700, [ 473,  617,  724,  809,  890,  964]],
    [ 2800, [ 486,  633,  744,  831,  914,  989]],
    [ 2900, [ 498,  649,  762,  852,  937, 1015]],
    [ 3000, [ 510,  665,  781,  873,  960, 1040]],
    [ 3100, [ 522,  681,  800,  893,  982, 1064]],
    [ 3200, [ 534,  696,  818,  914, 1005, 1088]],
    [ 3300, [ 545,  711,  836,  934, 1027, 1112]],
    [ 3400, [ 557,  727,  853,  953, 1049, 1135]],
    [ 3500, [ 568,  741,  871,  973, 1070, 1158]],
    [ 3600, [ 579,  756,  888,  992, 1091, 1181]],
    [ 3700, [ 590,  770,  905, 1010, 1111, 1203]],
    [ 3800, [ 601,  785,  921, 1029, 1132, 1225]],
    [ 3900, [ 611,  799,  938, 1047, 1152, 1247]],
    [ 4000, [ 622,  813,  954, 1065, 1172, 1269]],
    [ 4100, [ 632,  826,  970, 1083, 1191, 1290]],
    [ 4200, [ 642,  839,  986, 1100, 1210, 1311]],
    [ 4300, [ 652,  852, 1001, 1117, 1229, 1331]],
    [ 4400, [ 661,  864, 1015, 1133, 1247, 1350]],
    [ 4500, [ 671,  876, 1029, 1149, 1264, 1369]],
    [ 4600, [ 680,  888, 1044, 1165, 1282, 1388]],
    [ 4700, [ 689,  900, 1058, 1181, 1299, 1407]],
    [ 4800, [ 698,  912, 1072, 1196, 1316, 1425]],
    [ 4900, [ 707,  924, 1086, 1212, 1334, 1444]],
    [ 5000, [ 716,  936, 1100, 1227, 1351, 1463]],
    [ 5500, [ 760,  993, 1167, 1303, 1433, 1552]],
    [ 6000, [ 802, 1048, 1232, 1375, 1513, 1638]],
    [ 6500, [ 841, 1100, 1292, 1443, 1587, 1718]],
    [ 7000, [ 878, 1148, 1349, 1505, 1656, 1793]],
    [ 7500, [ 913, 1193, 1403, 1565, 1722, 1864]],
    [ 8000, [ 945, 1236, 1453, 1621, 1784, 1931]],
    [ 8500, [ 975, 1276, 1500, 1674, 1841, 1994]],
    [ 9000, [1003, 1313, 1543, 1722, 1894, 2051]],
    [ 9500, [1030, 1349, 1585, 1769, 1946, 2106]],
    [10000, [1056, 1382, 1625, 1813, 1995, 2159]],
    [11000, [1106, 1448, 1702, 1900, 2090, 2262]],
    [12000, [1153, 1509, 1774, 1980, 2178, 2358]],
    [13000, [1195, 1564, 1840, 2053, 2258, 2444]],
    [14000, [1234, 1615, 1900, 2121, 2332, 2525]],
    [15000, [1270, 1663, 1956, 2183, 2402, 2599]],
    [16000, [1304, 1707, 2008, 2241, 2465, 2668]],
    [17000, [1335, 1748, 2056, 2295, 2525, 2733]],
    [18000, [1365, 1787, 2102, 2347, 2581, 2794]],
    [19000, [1393, 1824, 2145, 2395, 2634, 2851]],
    [20000, [1419, 1859, 2186, 2441, 2685, 2905]],
    [22000, [1469, 1925, 2264, 2528, 2780, 3008]],
    [25000, [1538, 2016, 2371, 2647, 2912, 3151]],
    [27000, [1579, 2070, 2434, 2718, 2990, 3235]],
    [30000, [1633, 2141, 2518, 2812, 3093, 3347]],
];

/**
 * Look up the Basic Child Support Obligation for a given
 * combined adjusted gross income and number of children.
 *
 * Interpolates linearly between the nearest table rows.
 * Returns 0 for invalid inputs or income below the table minimum.
 * For income above the max, scales by the ratio (approximation).
 */
function lookupAZSchedule(combinedIncome, numChildren) {
    if (!combinedIncome || combinedIncome < 950 || !numChildren) return 0;
    numChildren = Math.min(Math.max(parseInt(numChildren) || 1, 1), 6);
    const colIdx = numChildren - 1;

    // Above max: scale from the top row using the ratio
    const top = AZ_CS_SCHEDULE[AZ_CS_SCHEDULE.length - 1];
    if (combinedIncome >= top[0]) {
        // AZ guidelines cap basic obligation growth above $30k
        // Use the top row value (guidelines suggest discretion above this)
        return top[1][colIdx];
    }

    // Find the two bracketing rows
    for (let i = 0; i < AZ_CS_SCHEDULE.length - 1; i++) {
        const row = AZ_CS_SCHEDULE[i];
        const next = AZ_CS_SCHEDULE[i + 1];
        if (combinedIncome >= row[0] && combinedIncome < next[0]) {
            // Linear interpolation
            const x0 = row[0], x1 = next[0];
            const y0 = row[1][colIdx], y1 = next[1][colIdx];
            const ratio = (combinedIncome - x0) / (x1 - x0);
            return Math.round(y0 + (y1 - y0) * ratio);
        }
    }

    return 0;
}

// ── Worksheet Pre-Population ────────────────────────────────

/**
 * Auto-populate Line 13 (Gross Monthly Income) on the worksheet
 * from the employment income entered in Steps 7 and 8.
 *
 * Maps Petitioner/Respondent → Father/Mother based on the
 * petitioner's role selected in Step 3.
 *
 * Only overwrites the worksheet fields if they're empty or
 * were previously set by this same function (tracked via
 * data-from-employment flag).
 */
function prepopulateWorksheetIncome() {
    // Get incomes from Steps 7 & 8
    const respIncomeEl = document.querySelector('[name="resp_monthly_income"]');
    const petIncomeEl = document.querySelector('[name="pet_monthly_income"]');
    const respIncome = respIncomeEl ? respIncomeEl.value.replace(/[$,\s]/g, '').trim() : '';
    const petIncome = petIncomeEl ? petIncomeEl.value.replace(/[$,\s]/g, '').trim() : '';

    // Determine petitioner's role (mother/father) from Step 3
    const petRoleEl = document.querySelector('[name="pet_role"]');
    const petRole = petRoleEl ? petRoleEl.value : 'mother';

    // Map pet/resp → father/mother
    let fatherIncome = '', motherIncome = '';
    if (petRole === 'mother') {
        motherIncome = petIncome;
        fatherIncome = respIncome;
    } else if (petRole === 'father') {
        fatherIncome = petIncome;
        motherIncome = respIncome;
    } else {
        // Guardian/Other — use petitioner as mother by convention
        motherIncome = petIncome;
        fatherIncome = respIncome;
    }

    // Apply to worksheet fields if they're empty or previously auto-filled
    const fatherGrossEl = document.querySelector('[name="ws_father_gross"]');
    const motherGrossEl = document.querySelector('[name="ws_mother_gross"]');

    if (fatherGrossEl && fatherIncome) {
        const current = fatherGrossEl.value.trim();
        if (current === '' || fatherGrossEl.dataset.fromEmployment === '1') {
            fatherGrossEl.value = fatherIncome;
            fatherGrossEl.dataset.fromEmployment = '1';
        }
    }

    if (motherGrossEl && motherIncome) {
        const current = motherGrossEl.value.trim();
        if (current === '' || motherGrossEl.dataset.fromEmployment === '1') {
            motherGrossEl.value = motherIncome;
            motherGrossEl.dataset.fromEmployment = '1';
        }
    }
}

// ── Worksheet Live Calculation Engine ───────────────────────

/**
 * Read a worksheet numeric field, stripping $ and commas.
 * Returns 0 for empty/invalid fields.
 */
function wsNum(name) {
    const el = document.querySelector(`[name="${name}"]`);
    if (!el) return 0;
    const raw = (el.value || '').replace(/[$,%\s]/g, '');
    const num = parseFloat(raw);
    return isNaN(num) ? 0 : num;
}

/** Format a number as dollar string (without $ sign for field value) */
function fmtMoney(num) {
    if (num === 0) return '0.00';
    return num.toFixed(2);
}

/** Format a number as percentage string (1 decimal) */
function fmtPct(num) {
    return (Math.round(num * 10) / 10).toString();
}

/** Set a field value only if it was auto-calculated (marked) or empty */
function setCalcField(name, value) {
    const el = document.querySelector(`[name="${name}"]`);
    if (!el) return;
    // Always overwrite calculated fields when live-calculating
    el.value = value;
    el.classList.add('auto-calculated');
}

/**
 * Recalculate all derived worksheet fields from inputs.
 * Called on every input change in step 9.
 */
function calculateWorksheet() {
    // ── Line 19: Adjusted Gross Monthly Income ──
    // = Gross - Spousal Paid + Spousal Received - Other CS Paid
    const fatherGross = wsNum('ws_father_gross');
    const motherGross = wsNum('ws_mother_gross');

    const fatherAdjusted = fatherGross
        - wsNum('ws_father_spousal_paid')
        + wsNum('ws_father_spousal_received')
        - wsNum('ws_father_other_cs');

    const motherAdjusted = motherGross
        - wsNum('ws_mother_spousal_paid')
        + wsNum('ws_mother_spousal_received')
        - wsNum('ws_mother_other_cs');

    setCalcField('ws_father_adjusted', fmtMoney(Math.max(0, fatherAdjusted)));
    setCalcField('ws_mother_adjusted', fmtMoney(Math.max(0, motherAdjusted)));

    // ── Line 20: Combined Adjusted Gross Income ──
    const combined = Math.max(0, fatherAdjusted) + Math.max(0, motherAdjusted);
    setCalcField('ws_combined_adjusted', fmtMoney(combined));

    // ── Line 21: Basic Child Support Obligation ──
    // Auto-lookup from AZ Child Support Schedule (Appendix A).
    // User can override if a different value is needed.
    const numChildren = wsNum('ws_num_minor_children') || 1;
    const basicObligationEl = document.querySelector('[name="ws_basic_obligation"]');
    const userEnteredBasic = basicObligationEl && !basicObligationEl.classList.contains('auto-calculated')
        && basicObligationEl.value.trim() !== '' && !basicObligationEl.dataset.autoLookup;

    let basicObligation;
    if (userEnteredBasic) {
        // User manually set it — respect their value
        basicObligation = wsNum('ws_basic_obligation');
    } else {
        // Auto-lookup from schedule
        basicObligation = lookupAZSchedule(combined, numChildren);
        setCalcField('ws_basic_obligation', fmtMoney(basicObligation));
        if (basicObligationEl) basicObligationEl.dataset.autoLookup = '1';
    }

    // ── Line 22: Adjustment for children over 12 ──
    // AZ Guidelines 6B: +10% per child over 12, but not more than the number
    // of children over 12 out of total, calculated as:
    //   (num_over_12 / num_children) × 0.10 × basic_obligation
    const numOver12 = wsNum('ws_num_children_over_12');
    const over12Adjustment = numChildren > 0
        ? (numOver12 / numChildren) * 0.10 * basicObligation
        : 0;

    // ── Line 27: Subtotal of added costs (per parent) ──
    // = Medical Ins + Childcare + Education + Extraordinary
    // (Currently only collecting Medical + Childcare from form)
    const fatherSubtotal = wsNum('ws_father_medical_ins') + wsNum('ws_father_childcare');
    const motherSubtotal = wsNum('ws_mother_medical_ins') + wsNum('ws_mother_childcare');

    // ── Line 28: Total Adjustments for Costs ──
    const totalAdjustments = fatherSubtotal + motherSubtotal;

    // ── Line 29: Total Child Support Obligation ──
    // = Basic + Over-12 adjustment + Total Adjustments
    const totalObligation = basicObligation + over12Adjustment + totalAdjustments;
    setCalcField('ws_total_obligation', fmtMoney(totalObligation));

    // ── Line 30: Proportionate percentages ──
    let fatherPct = 0, motherPct = 0;
    if (combined > 0) {
        fatherPct = (Math.max(0, fatherAdjusted) / combined) * 100;
        motherPct = (Math.max(0, motherAdjusted) / combined) * 100;
    }
    setCalcField('ws_father_pct', fmtPct(fatherPct));
    setCalcField('ws_mother_pct', fmtPct(motherPct));

    // ── Line 31: Each parent's proportionate share ──
    const fatherShare = totalObligation * (fatherPct / 100);
    const motherShare = totalObligation * (motherPct / 100);
    setCalcField('ws_father_share', fmtMoney(fatherShare));
    setCalcField('ws_mother_share', fmtMoney(motherShare));

    // ── Line 32: Less paying parent's costs ──
    // The paying parent gets credit for costs they already pay (Line 27 subtotal).
    // Determine who pays: whoever has the higher share (more income).
    const paidBy = document.querySelector('[name="ws_cs_paid_by"]:checked');
    let payorIsFather = true;
    if (paidBy) {
        payorIsFather = paidBy.value === 'father';
    } else {
        payorIsFather = fatherShare >= motherShare;
    }

    const payorCosts = payorIsFather ? fatherSubtotal : motherSubtotal;

    // ── Line 33: Parenting time adjustment ──
    // Uses the non-custodial parent's overnight count and Table A or B.
    //
    // AZ Guidelines Table A (non-custodial <110 days):
    //   Days:   0-36  37-55  56-73  74-91  92-109
    //   Pct:      0%    0.5%   1.0%   1.5%   2.0%
    //
    // AZ Guidelines Table B (non-custodial 110+ days):
    //   Days: 110-115 116-120 121-125 126-130 131-135 136-140 141-145 146-150 151-155 156-160 161-165 166-170 171-175 176-182
    //   Pct:   2.5%    3.0%    3.5%    4.0%    4.5%    5.0%    5.5%    6.0%    6.5%    7.0%    7.5%    8.0%    8.5%    9.0%
    //
    // The percentage is applied to the total obligation (Line 29) and credited to the non-custodial parent.

    const fatherDays = parseInt(document.querySelector('[name="pt_total_father"]')?.value || '0') || 0;
    const motherDays = parseInt(document.querySelector('[name="pt_total_mother"]')?.value || '0') || 0;
    const nonCustodialDays = Math.min(fatherDays, motherDays);
    const tableUsed = document.querySelector('[name="ws_parenting_table"]')?.value || 'A';

    let parentingTimePct = 0;
    if (nonCustodialDays >= 176) parentingTimePct = 9.0;
    else if (nonCustodialDays >= 171) parentingTimePct = 8.5;
    else if (nonCustodialDays >= 166) parentingTimePct = 8.0;
    else if (nonCustodialDays >= 161) parentingTimePct = 7.5;
    else if (nonCustodialDays >= 156) parentingTimePct = 7.0;
    else if (nonCustodialDays >= 151) parentingTimePct = 6.5;
    else if (nonCustodialDays >= 146) parentingTimePct = 6.0;
    else if (nonCustodialDays >= 141) parentingTimePct = 5.5;
    else if (nonCustodialDays >= 136) parentingTimePct = 5.0;
    else if (nonCustodialDays >= 131) parentingTimePct = 4.5;
    else if (nonCustodialDays >= 126) parentingTimePct = 4.0;
    else if (nonCustodialDays >= 121) parentingTimePct = 3.5;
    else if (nonCustodialDays >= 116) parentingTimePct = 3.0;
    else if (nonCustodialDays >= 110) parentingTimePct = 2.5;
    else if (nonCustodialDays >= 92) parentingTimePct = 2.0;
    else if (nonCustodialDays >= 74) parentingTimePct = 1.5;
    else if (nonCustodialDays >= 56) parentingTimePct = 1.0;
    else if (nonCustodialDays >= 37) parentingTimePct = 0.5;
    else parentingTimePct = 0;

    const parentingTimeCredit = totalObligation * (parentingTimePct / 100);

    // Credit goes to the non-custodial parent (reduces their obligation)
    // The non-custodial parent is the payor (who has fewer overnights)
    const fatherPTCredit = (fatherDays <= motherDays) ? parentingTimeCredit : 0;
    const motherPTCredit = (motherDays < fatherDays) ? parentingTimeCredit : 0;

    // ── Line 34: Adjustments subtotal ──
    const fatherAdjSubtotal = payorCosts + fatherPTCredit;
    const motherAdjSubtotal = (payorIsFather ? 0 : payorCosts) + motherPTCredit;

    // ── Line 35: Preliminary Child Support Amount ──
    let preliminaryCS = 0;
    if (payorIsFather) {
        preliminaryCS = fatherShare - fatherAdjSubtotal;
    } else {
        preliminaryCS = motherShare - motherAdjSubtotal;
    }
    preliminaryCS = Math.max(0, preliminaryCS);
    setCalcField('ws_preliminary_cs', fmtMoney(preliminaryCS));

    // ── Line 37: Final CS Amount ──
    // For a simple calculation (no self-support reserve test adjustment needed)
    // the final amount equals the preliminary amount.
    setCalcField('ws_final_cs_amount', fmtMoney(preliminaryCS));

    // ── Propagate to Step 5 ──
    // Auto-fill the Step 5 monthly support amount so it appears on the
    // Petition and Child Support Order pages. Only if Step 5 field is empty
    // or was previously auto-filled from the worksheet.
    const monthlyAmountEl = document.querySelector('[name="monthly_amount"]');
    if (monthlyAmountEl && preliminaryCS > 0) {
        const current = monthlyAmountEl.value.trim();
        if (current === '' || monthlyAmountEl.dataset.fromWorksheet === '1') {
            monthlyAmountEl.value = fmtMoney(preliminaryCS);
            monthlyAmountEl.dataset.fromWorksheet = '1';
        }
    }

    // Auto-set the Step 5 "who pays" dropdown based on worksheet
    const supportPayorEl = document.querySelector('[name="support_payor"]');
    if (supportPayorEl && paidBy) {
        // Determine if payor is petitioner or respondent based on relationship
        const petRoleEl = document.querySelector('[name="pet_role"]');
        const petRole = petRoleEl ? petRoleEl.value : 'mother';
        const payorParent = paidBy.value; // 'father' or 'mother'
        if (payorParent === petRole) {
            supportPayorEl.value = 'pet';
        } else {
            supportPayorEl.value = 'resp';
        }
    }
}

/** Attach live-calc listeners to all worksheet input fields */
function initWorksheetCalculation() {
    const inputFields = [
        'ws_father_gross', 'ws_mother_gross',
        'ws_father_spousal_paid', 'ws_mother_spousal_paid',
        'ws_father_spousal_received', 'ws_mother_spousal_received',
        'ws_father_other_cs', 'ws_mother_other_cs',
        'ws_basic_obligation',
        'ws_father_medical_ins', 'ws_mother_medical_ins',
        'ws_father_childcare', 'ws_mother_childcare',
        'ws_num_children_over_12',
    ];
    inputFields.forEach(name => {
        const el = document.querySelector(`[name="${name}"]`);
        if (el) {
            el.addEventListener('input', calculateWorksheet);
        }
    });
    // Also recalc when "paid by" radio changes
    document.querySelectorAll('[name="ws_cs_paid_by"]').forEach(el => {
        el.addEventListener('change', calculateWorksheet);
    });
}

// ── Parenting Time Schedule Builder ──────────────────────────

function calcParentingTime() {
    // Skip if override is active
    if (document.getElementById('pt_override_check')?.checked) return;

    const num = (name) => parseInt(document.querySelector(`[name="${name}"]`)?.value || '0') || 0;

    // Regular weekly schedule → annualized
    const weeknightsFather = num('pt_weeknights_father');
    const weeknightsMother = num('pt_weeknights_mother');
    const weekendsFather = num('pt_weekends_father');
    const weekendsMother = num('pt_weekends_mother');

    // Weekly overnights × 52 weeks
    const regularFather = (weeknightsFather * 52) + (weekendsFather * 12); // 12 months of weekends
    const regularMother = (weeknightsMother * 52) + (weekendsMother * 12);

    // Holiday & break additions
    const summerFather = num('pt_summer_father');
    const summerMother = num('pt_summer_mother');
    const winterFather = num('pt_winter_father');
    const winterMother = num('pt_winter_mother');
    const springFather = num('pt_spring_father');
    const springMother = num('pt_spring_mother');
    const holidaysFather = num('pt_holidays_father');
    const holidaysMother = num('pt_holidays_mother');

    const holidayTotalFather = summerFather + winterFather + springFather + holidaysFather;
    const holidayTotalMother = summerMother + winterMother + springMother + holidaysMother;

    // During summer/break, the child is with the break-parent INSTEAD of regular schedule.
    // So the total = regular + holiday additions, but capped at 365 combined.
    let totalFather = regularFather + holidayTotalFather;
    let totalMother = regularMother + holidayTotalMother;

    // Normalize so they sum to 365
    const rawTotal = totalFather + totalMother;
    if (rawTotal > 0 && rawTotal !== 365) {
        const scale = 365 / rawTotal;
        totalFather = Math.round(totalFather * scale);
        totalMother = 365 - totalFather;  // Ensure exact 365
    }

    // Ensure non-negative
    totalFather = Math.max(0, totalFather);
    totalMother = Math.max(0, totalMother);

    // Update displays
    updateParentingDisplay(regularFather, regularMother, holidayTotalFather, holidayTotalMother, totalFather, totalMother);
}

function applyParentingOverride() {
    const overrideFather = parseInt(document.querySelector('[name="pt_override_father"]')?.value || '0') || 0;
    const overrideMother = parseInt(document.querySelector('[name="pt_override_mother"]')?.value || '0') || 0;
    updateParentingDisplay(0, 0, 0, 0, overrideFather, overrideMother);
}

function toggleParentingOverride() {
    const checked = document.getElementById('pt_override_check').checked;
    const section = document.getElementById('pt-override-section');
    if (checked) {
        section.classList.add('visible');
        applyParentingOverride();
    } else {
        section.classList.remove('visible');
        calcParentingTime();
    }
}

function updateParentingDisplay(regFather, regMother, holFather, holMother, totalFather, totalMother) {
    // Update subtotal displays
    const regEl = document.getElementById('regular-subtotal');
    if (regEl) {
        regEl.innerHTML = `Regular schedule: <strong>Father ~${regFather} nights/year</strong>, <strong>Mother ~${regMother} nights/year</strong>`;
    }
    const holEl = document.getElementById('holiday-subtotal');
    if (holEl) {
        holEl.innerHTML = `Holiday/break additions: <strong>Father +${holFather} nights</strong>, <strong>Mother +${holMother} nights</strong>`;
    }

    // Update totals
    document.querySelector('[name="pt_total_father"]').value = totalFather;
    document.querySelector('[name="pt_total_mother"]').value = totalMother;

    const combined = totalFather + totalMother;

    // Status display
    const statusEl = document.getElementById('parenting-time-status');
    if (combined === 365) {
        statusEl.className = 'info-box success';
        statusEl.innerHTML = `<strong>Total: ${combined} / 365 days</strong> — Father: ${totalFather} overnights (${(totalFather/365*100).toFixed(1)}%), Mother: ${totalMother} overnights (${(totalMother/365*100).toFixed(1)}%)`;
    } else if (combined > 0) {
        statusEl.className = 'info-box warning';
        statusEl.innerHTML = `<strong>Total: ${combined} / 365 days</strong> — ${combined > 365 ? 'Over' : 'Under'} by ${Math.abs(365 - combined)} days. Will be normalized to 365.`;
    } else {
        statusEl.className = 'info-box note';
        statusEl.textContent = 'Enter the parenting time schedule above.';
    }

    // Update hidden fields for the worksheet
    // Determine time-sharing arrangement label
    const tsField = document.querySelector('[name="ws_time_sharing"]');
    if (totalFather > 0 && totalMother > 0) {
        if (Math.abs(totalFather - totalMother) <= 10) {
            tsField.value = 'equal';
        } else if (totalFather > totalMother) {
            tsField.value = 'mostly_father';
        } else {
            tsField.value = 'mostly_mother';
        }
    }

    // Determine Table A vs Table B
    // Non-custodial parent = the one with fewer days
    const nonCustodialDays = Math.min(totalFather, totalMother);
    const tableField = document.querySelector('[name="ws_parenting_table"]');
    tableField.value = nonCustodialDays >= 110 ? 'B' : 'A';

    // Trigger worksheet recalculation
    if (typeof calculateWorksheet === 'function') {
        calculateWorksheet();
    }
}

// ── Insurance Cost Toggle ───────────────────────────────────

function toggleInsuranceCost() {
    const val = document.querySelector('[name="who_provides_insurance"]').value;
    const group = document.getElementById('insurance-cost-group');
    group.style.display = (val === 'none' || val === 'state') ? 'none' : 'block';
}

// ── Validation ──────────────────────────────────────────────

function validateStep(step) {
    const panel = document.getElementById(`step${step}`);
    let valid = true;

    // Clear previous errors
    panel.querySelectorAll('.error').forEach(el => el.classList.remove('error'));
    panel.querySelectorAll('.field-error').forEach(el => el.classList.remove('visible'));

    // Check required fields
    panel.querySelectorAll('input[required], select[required]').forEach(input => {
        // Skip hidden fields
        if (input.closest('.conditional') && !input.closest('.conditional').classList.contains('visible')) return;
        if (input.closest('.hidden')) return;

        if (!input.value.trim()) {
            input.classList.add('error');
            const err = input.parentElement.querySelector('.field-error');
            if (err) err.classList.add('visible');
            valid = false;
        }
    });

    // Check format validators
    panel.querySelectorAll('[data-validate]').forEach(input => {
        if (!input.value.trim()) return; // Skip empty optional fields
        if (input.closest('.conditional') && !input.closest('.conditional').classList.contains('visible')) return;

        const type = input.dataset.validate;
        let fieldValid = true;

        if (type === 'date') {
            fieldValid = /^\d{2}\/\d{2}\/\d{4}$/.test(input.value.trim());
        } else if (type === 'zip') {
            fieldValid = /^\d{5}(-\d{4})?$/.test(input.value.trim());
        } else if (type === 'dollar') {
            const cleaned = input.value.replace(/[$,]/g, '').trim();
            fieldValid = !isNaN(parseFloat(cleaned));
        } else if (type === 'percent') {
            const cleaned = input.value.replace(/%/g, '').trim();
            const num = parseFloat(cleaned);
            fieldValid = !isNaN(num) && num >= 0 && num <= 100;
        }

        if (!fieldValid) {
            input.classList.add('error');
            const err = input.parentElement.querySelector('.field-error');
            if (err) err.classList.add('visible');
            valid = false;
        }
    });

    if (!valid) {
        // Scroll to first error
        const firstError = panel.querySelector('.error');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstError.focus();
        }
    }

    return valid;
}

// ── Collect Form Data ───────────────────────────────────────

function getVal(name) {
    const el = document.querySelector(`[name="${name}"]`);
    if (!el) return '';
    if (el.type === 'radio') {
        const checked = document.querySelector(`[name="${name}"]:checked`);
        return checked ? checked.value : '';
    }
    return (el.value || '').trim();
}

function collectFormData() {
    const pet_first = getVal('pet_first');
    const pet_middle = getVal('pet_middle');
    const pet_last = getVal('pet_last');
    const resp_first = getVal('resp_first');
    const resp_middle = getVal('resp_middle');
    const resp_last = getVal('resp_last');
    const child_first = getVal('child_first');
    const child_middle = getVal('child_middle');
    const child_last = getVal('child_last');

    // Build child address
    const livesWithVal = getVal('child_lives_with');
    let child_address, child_city, child_state, child_zip;
    if (livesWithVal === 'pet') {
        child_address = getVal('pet_address');
        child_city = getVal('pet_city');
        child_state = getVal('pet_state');
        child_zip = getVal('pet_zip');
    } else if (livesWithVal === 'resp') {
        child_address = getVal('resp_address');
        child_city = getVal('resp_city');
        child_state = getVal('resp_state');
        child_zip = getVal('resp_zip');
    } else {
        child_address = getVal('child_address');
        child_city = getVal('child_city');
        child_state = getVal('child_state');
        child_zip = getVal('child_zip');
    }

    // Travel split
    let pet_travel_pct, resp_travel_pct;
    if (getVal('travel_same_split') === 'yes') {
        pet_travel_pct = getVal('pet_medical_pct');
        resp_travel_pct = getVal('resp_medical_pct');
    } else {
        pet_travel_pct = getVal('pet_travel_pct');
        resp_travel_pct = getVal('resp_travel_pct');
    }

    return {
        petitioner: {
            first_name: pet_first,
            middle_name: pet_middle,
            last_name: pet_last,
            full_name: [pet_first, pet_middle, pet_last].filter(Boolean).join(' '),
            dob: getVal('pet_dob'),
            ssn: getVal('pet_ssn'),
            dl_number: getVal('pet_dl'),
            phone: getVal('pet_phone'),
            email: getVal('pet_email'),
            address: getVal('pet_address'),
            city: getVal('pet_city'),
            state: getVal('pet_state'),
            zip: getVal('pet_zip'),
            gender: getVal('pet_gender'),
            has_attorney: getVal('pet_has_attorney') === 'yes',
            attorney_name: getVal('pet_attorney_name'),
            attorney_bar: getVal('pet_attorney_bar'),
            attorney_address: getVal('pet_attorney_address'),
            attorney_phone: getVal('pet_attorney_phone'),
        },
        respondent: {
            first_name: resp_first,
            middle_name: resp_middle,
            last_name: resp_last,
            full_name: [resp_first, resp_middle, resp_last].filter(Boolean).join(' '),
            dob: getVal('resp_dob'),
            ssn: getVal('resp_ssn'),
            dl_number: getVal('resp_dl'),
            phone: getVal('resp_phone'),
            email: getVal('resp_email'),
            address: getVal('resp_address'),
            city: getVal('resp_city'),
            state: getVal('resp_state'),
            zip: getVal('resp_zip'),
            gender: getVal('resp_gender'),
        },
        relationship: {
            petitioner_role: getVal('pet_role'),
            respondent_role: getVal('resp_role'),
            on_birth_cert: getVal('on_birth_cert') === 'yes',
            paternity_established: getVal('paternity_established') === 'yes',
            paternity_acknowledged: getVal('paternity_acknowledged') === 'yes',
            contesting_paternity: getVal('contesting_paternity') === 'yes',
            were_married: getVal('were_married') === 'yes',
            still_married: getVal('still_married') === 'yes',
        },
        child: {
            first_name: child_first,
            middle_name: child_middle,
            last_name: child_last,
            full_name: [child_first, child_middle, child_last].filter(Boolean).join(' '),
            dob: getVal('child_dob'),
            ssn: getVal('child_ssn'),
            gender: getVal('child_gender'),
            lives_with: livesWithVal,
            address: child_address,
            city: child_city,
            state: child_state,
            zip: child_zip,
        },
        support: {
            monthly_amount: getVal('monthly_amount').replace(/[$,]/g, ''),
            payor: getVal('support_payor'),
            pet_medical_pct: getVal('pet_medical_pct').replace(/%/g, ''),
            resp_medical_pct: getVal('resp_medical_pct').replace(/%/g, ''),
            pet_travel_pct: (pet_travel_pct || '').replace(/%/g, ''),
            resp_travel_pct: (resp_travel_pct || '').replace(/%/g, ''),
            who_provides_insurance: getVal('who_provides_insurance'),
            insurance_cost: getVal('insurance_cost').replace(/[$,]/g, ''),
        },
        arrears: {
            requesting_past_support: getVal('requesting_arrears') === 'yes',
            past_support_from: getVal('arrears_from'),
            past_support_amount: getVal('arrears_amount').replace(/[$,]/g, ''),
            past_support_notes: getVal('arrears_notes'),
        },
        employment: {
            is_employed: getVal('resp_employed') === 'yes',
            employer_name: getVal('resp_employer_name'),
            employment_type: getVal('resp_employment_type'),
            employer_address: getVal('resp_employer_address'),
            employer_city: getVal('resp_employer_city'),
            employer_state: getVal('resp_employer_state'),
            employer_zip: getVal('resp_employer_zip'),
            employer_phone: getVal('resp_employer_phone'),
            payroll_address: getVal('resp_payroll_address'),
            job_title: getVal('resp_job_title'),
            last_known_employer: getVal('resp_last_employer'),
            resp_monthly_income: getVal('resp_monthly_income').replace(/[$,]/g, ''),
        },
        petitioner_employment: {
            is_employed: getVal('pet_employed') === 'yes',
            employer_name: getVal('pet_employer_name'),
            employment_type: getVal('pet_employment_type'),
            monthly_income: getVal('pet_monthly_income').replace(/[$,]/g, ''),
        },
        worksheet: {
            time_sharing: getVal('ws_time_sharing'),
            parenting_table: getVal('ws_parenting_table') || 'A',
            father_overnights: getVal('pt_total_father') || '0',
            mother_overnights: getVal('pt_total_mother') || '0',
            other_parent_income_type: getVal('ws_income_type'),
            num_minor_children: getVal('ws_num_minor_children') || '1',
            num_children_over_12: getVal('ws_num_children_over_12') || '0',
            father_gross_monthly: getVal('ws_father_gross').replace(/[$,]/g, ''),
            mother_gross_monthly: getVal('ws_mother_gross').replace(/[$,]/g, ''),
            father_spousal_paid: getVal('ws_father_spousal_paid').replace(/[$,]/g, '') || '0',
            mother_spousal_paid: getVal('ws_mother_spousal_paid').replace(/[$,]/g, '') || '0',
            father_spousal_received: getVal('ws_father_spousal_received').replace(/[$,]/g, '') || '0',
            mother_spousal_received: getVal('ws_mother_spousal_received').replace(/[$,]/g, '') || '0',
            father_other_cs_paid: getVal('ws_father_other_cs').replace(/[$,]/g, '') || '0',
            mother_other_cs_paid: getVal('ws_mother_other_cs').replace(/[$,]/g, '') || '0',
            father_adjusted_gross: getVal('ws_father_adjusted').replace(/[$,]/g, ''),
            mother_adjusted_gross: getVal('ws_mother_adjusted').replace(/[$,]/g, ''),
            combined_adjusted_gross: getVal('ws_combined_adjusted').replace(/[$,]/g, ''),
            basic_cs_obligation: getVal('ws_basic_obligation').replace(/[$,]/g, ''),
            father_medical_insurance: getVal('ws_father_medical_ins').replace(/[$,]/g, '') || '0',
            mother_medical_insurance: getVal('ws_mother_medical_ins').replace(/[$,]/g, '') || '0',
            father_childcare: getVal('ws_father_childcare').replace(/[$,]/g, '') || '0',
            mother_childcare: getVal('ws_mother_childcare').replace(/[$,]/g, '') || '0',
            total_cs_obligation: getVal('ws_total_obligation').replace(/[$,]/g, ''),
            father_pct: getVal('ws_father_pct').replace(/%/g, ''),
            mother_pct: getVal('ws_mother_pct').replace(/%/g, ''),
            father_share: getVal('ws_father_share').replace(/[$,]/g, ''),
            mother_share: getVal('ws_mother_share').replace(/[$,]/g, ''),
            father_preliminary_cs: getVal('ws_cs_paid_by') === 'father' ? getVal('ws_preliminary_cs').replace(/[$,]/g, '') : '',
            mother_preliminary_cs: getVal('ws_cs_paid_by') === 'mother' ? getVal('ws_preliminary_cs').replace(/[$,]/g, '') : '',
            cs_paid_by: getVal('ws_cs_paid_by'),
            father_cs_amount: getVal('ws_cs_paid_by') === 'father' ? getVal('ws_final_cs_amount').replace(/[$,]/g, '') : '',
            mother_cs_amount: getVal('ws_cs_paid_by') === 'mother' ? getVal('ws_final_cs_amount').replace(/[$,]/g, '') : '',
        },
        options: {
            request_tax_exemption: getVal('request_tax_exemption') === 'yes',
            tax_exemption_to: getVal('tax_exemption_to'),
            tax_conditional: getVal('tax_conditional') === 'yes',
            address_protection: getVal('address_protection') === 'yes',
            safe_address: getVal('safe_address'),
            has_start_date: getVal('has_start_date') === 'yes',
            start_date: getVal('start_date'),
        },
        disclosures: {
            public_assistance: getVal('public_assistance') === 'yes',
            dcse_case: getVal('dcse_case') === 'yes',
            current_other_cases: getVal('current_other_cases') === 'yes',
            past_other_cases: getVal('past_other_cases') === 'yes',
            wife_pregnant: getVal('wife_pregnant') === 'yes',
            served_by_publication: getVal('served_by_publication') === 'yes',
        },
        jurisdiction: {
            resident: document.querySelector('[name="juris_resident"]')?.checked || false,
            serve: document.querySelector('[name="juris_serve"]')?.checked || false,
            agrees: document.querySelector('[name="juris_agrees"]')?.checked || false,
            lived_with_child: document.querySelector('[name="juris_lived_with_child"]')?.checked || false,
            prebirth: document.querySelector('[name="juris_prebirth"]')?.checked || false,
            child_lives: document.querySelector('[name="juris_child_lives"]')?.checked || false,
        },
        legal: {
            paternity_method: getVal('paternity_method'),
            no_current_order: getVal('no_current_order') === 'yes',
            voluntary_payments: getVal('voluntary_payments') === 'yes',
        },
        venue: {
            county: getVal('venue_county'),
            state: 'Arizona',
            venue_basis: getVal('venue_basis'),
        },
    };
}

// ── Build Review Panel ──────────────────────────────────────

function buildReview() {
    const data = collectFormData();
    const container = document.getElementById('reviewContent');

    function rv(label, value) {
        const cls = value ? 'review-value' : 'review-value empty';
        const display = value || '(not provided)';
        return `<div class="review-row"><span class="review-label">${label}</span><span class="${cls}">${display}</span></div>`;
    }

    const livesWithLabels = { pet: 'Petitioner', resp: 'Respondent', other: 'Other' };
    const genderLabels = { m: 'Male', f: 'Female' };
    const roleLabels = { mother: 'Mother', father: 'Father', guardian: 'Legal Guardian', other: 'Other' };
    const empTypeLabels = { w2: 'W-2 Employee', '1099': 'Ind. Contractor', self: 'Self-employed', other: 'Other' };
    const insLabels = { pet: 'Petitioner', resp: 'Respondent', both: 'Both', none: 'Neither', state: 'AHCCCS' };

    let html = '';

    // Petitioner
    html += `<div class="review-block" onclick="goToStep(1)" style="cursor:pointer" title="Click to edit">
        <h3>Petitioner (Filing Party)</h3>
        ${rv('Name', data.petitioner.full_name)}
        ${rv('DOB', data.petitioner.dob)}
        ${rv('Gender', genderLabels[data.petitioner.gender])}
        ${rv('Address', `${data.petitioner.address}, ${data.petitioner.city}, ${data.petitioner.state} ${data.petitioner.zip}`)}
        ${rv('Phone', data.petitioner.phone)}
        ${rv('Email', data.petitioner.email)}
        ${rv('Attorney', data.petitioner.has_attorney ? data.petitioner.attorney_name : 'Self-represented')}
    </div>`;

    // Respondent
    html += `<div class="review-block" onclick="goToStep(2)" style="cursor:pointer" title="Click to edit">
        <h3>Respondent (Other Parent)</h3>
        ${rv('Name', data.respondent.full_name)}
        ${rv('DOB', data.respondent.dob)}
        ${rv('Gender', genderLabels[data.respondent.gender])}
        ${rv('Address', `${data.respondent.address}, ${data.respondent.city}, ${data.respondent.state} ${data.respondent.zip}`)}
        ${rv('Phone', data.respondent.phone)}
        ${rv('Email', data.respondent.email)}
    </div>`;

    // Relationship
    html += `<div class="review-block" onclick="goToStep(3)" style="cursor:pointer" title="Click to edit">
        <h3>Relationship</h3>
        ${rv('Pet. Role', roleLabels[data.relationship.petitioner_role])}
        ${rv('Resp. Role', roleLabels[data.relationship.respondent_role])}
        ${rv('On Birth Cert', data.relationship.on_birth_cert ? 'Yes' : 'No')}
        ${rv('Paternity Est.', data.relationship.paternity_established ? 'Yes' : 'No')}
        ${rv('Were Married', data.relationship.were_married ? 'Yes' : 'No')}
    </div>`;

    // Child
    html += `<div class="review-block" onclick="goToStep(4)" style="cursor:pointer" title="Click to edit">
        <h3>Child</h3>
        ${rv('Name', data.child.full_name)}
        ${rv('DOB', data.child.dob)}
        ${rv('Gender', genderLabels[data.child.gender])}
        ${rv('Lives With', livesWithLabels[data.child.lives_with])}
        ${rv('Address', `${data.child.address}, ${data.child.city}, ${data.child.state} ${data.child.zip}`)}
    </div>`;

    // Support
    html += `<div class="review-block" onclick="goToStep(5)" style="cursor:pointer" title="Click to edit">
        <h3>Child Support</h3>
        ${rv('Monthly Amount', data.support.monthly_amount ? `$${data.support.monthly_amount}` : '')}
        ${rv('Paid By', data.support.payor === 'resp' ? 'Respondent' : 'Petitioner')}
        ${rv('Medical Split', data.support.pet_medical_pct ? `${data.support.pet_medical_pct}% / ${data.support.resp_medical_pct}%` : '')}
        ${rv('Insurance', insLabels[data.support.who_provides_insurance])}
    </div>`;

    // Arrears
    if (data.arrears.requesting_past_support) {
        html += `<div class="review-block" onclick="goToStep(6)" style="cursor:pointer" title="Click to edit">
            <h3>Arrears</h3>
            ${rv('From Date', data.arrears.past_support_from)}
            ${rv('Amount', data.arrears.past_support_amount ? `$${data.arrears.past_support_amount}` : '')}
            ${rv('Notes', data.arrears.past_support_notes)}
        </div>`;
    }

    // Employment
    html += `<div class="review-block" onclick="goToStep(7)" style="cursor:pointer" title="Click to edit">
        <h3>Respondent Employment</h3>
        ${rv('Employed', data.employment.is_employed ? 'Yes' : 'No')}
        ${data.employment.is_employed ? rv('Employer', data.employment.employer_name) : ''}
        ${data.employment.is_employed ? rv('Type', empTypeLabels[data.employment.employment_type]) : ''}
        ${data.employment.resp_monthly_income ? rv('Monthly Income', `$${data.employment.resp_monthly_income}`) : ''}
    </div>`;

    // Worksheet
    const ws = data.worksheet;
    const tsLabels = { equal: 'Essentially Equal', mostly_father: 'Mostly with Father', mostly_mother: 'Mostly with Mother' };
    html += `<div class="review-block" onclick="goToStep(9)" style="cursor:pointer" title="Click to edit">
        <h3>Child Support Worksheet (Pages 15-17)</h3>
        ${rv('Time-Sharing', tsLabels[ws.time_sharing] || '')}
        ${rv('Parenting Time', ws.father_overnights && ws.mother_overnights ? `Father: ${ws.father_overnights} days, Mother: ${ws.mother_overnights} days (Table ${ws.parenting_table})` : '')}
        ${rv('Father Gross Monthly', ws.father_gross_monthly ? `$${ws.father_gross_monthly}` : '')}
        ${rv('Mother Gross Monthly', ws.mother_gross_monthly ? `$${ws.mother_gross_monthly}` : '')}
        ${rv('Combined Adjusted', ws.combined_adjusted_gross ? `$${ws.combined_adjusted_gross}` : '(auto)')}
        ${rv('Father %', ws.father_pct ? `${ws.father_pct}%` : '')}
        ${rv('Mother %', ws.mother_pct ? `${ws.mother_pct}%` : '')}
        ${rv('Total Obligation', ws.total_cs_obligation ? `$${ws.total_cs_obligation}` : '')}
        ${rv('CS Paid By', ws.cs_paid_by ? ws.cs_paid_by.charAt(0).toUpperCase() + ws.cs_paid_by.slice(1) : '')}
        ${rv('Final Amount', (ws.father_cs_amount || ws.mother_cs_amount) ? `$${ws.father_cs_amount || ws.mother_cs_amount}` : '')}
    </div>`;

    // Venue
    html += `<div class="review-block" onclick="goToStep(10)" style="cursor:pointer" title="Click to edit">
        <h3>Filing</h3>
        ${rv('County', data.venue.county)}
        ${rv('State', data.venue.state)}
    </div>`;

    container.innerHTML = html;
}

// ── Submit Form ─────────────────────────────────────────────

async function submitForm() {
    const data = collectFormData();

    // Show loading
    document.getElementById('loadingOverlay').classList.add('visible');

    try {
        const response = await fetch('/api/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        // Hide loading
        document.getElementById('loadingOverlay').classList.remove('visible');

        if (result.success) {
            showSuccess(result);
        } else {
            alert('Error: ' + (result.error || 'Unknown error occurred'));
        }
    } catch (err) {
        document.getElementById('loadingOverlay').classList.remove('visible');
        alert('Connection error: ' + err.message);
    }
}

function showSuccess(result) {
    document.getElementById('fieldsFilledCount').textContent =
        `${result.fields_filled} form fields filled successfully.`;

    const links = document.getElementById('downloadLinks');
    let html = '';

    if (result.pdf_editable) {
        html += `<li>
            <span>Editable Petition PDF</span>
            <a href="/api/download/${encodeURIComponent(result.pdf_editable)}" target="_blank">Download</a>
        </li>`;
    }
    if (result.pdf_filled) {
        html += `<li>
            <span>Filled Petition PDF</span>
            <a href="/api/download/${encodeURIComponent(result.pdf_filled)}" target="_blank">Download</a>
        </li>`;
    }
    if (result.validation) {
        html += `<li>
            <span>Validation Report</span>
            <a href="/api/download/${encodeURIComponent(result.validation)}" target="_blank">Download</a>
        </li>`;
    }
    if (result.json_file) {
        html += `<li>
            <span>Intake Data (JSON)</span>
            <a href="/api/download/${encodeURIComponent(result.json_file)}" target="_blank">Download</a>
        </li>`;
    }

    if (result.warnings && result.warnings.length > 0) {
        html += '<li style="background: #fefcbf; color: #975a16;">';
        html += '<span>Warnings: ' + result.warnings.join('; ') + '</span>';
        html += '</li>';
    }

    links.innerHTML = html;
    document.getElementById('successOverlay').classList.add('visible');
}
