# Project Charter: Smart Strap
**Author:** Adi Shalev  
**Domain:** Biomedical Engineering, Afeka College  

## 1. Project Overview & Objective
This project centers on the development of a smart watch strap utilizing Targeted Frequency Mapping technology. The primary objective is to engineer a personalized haptic wearable device that addresses the unique pathophysiological needs of individuals—particularly soldiers and veterans—suffering from Blast-Induced Hearing Loss (BIHL) and accompanying tinnitus.

## 2. Clinical Background & The Problem
Unlike continuous noise exposure, blast waves create a high-pressure shockwave that inflicts dual-impact damage to the ear.

* **Mechanical and Sensorineural Damage:** The overpressure can rupture the tympanic membrane and violently displace the basilar membrane, leading to the destruction of outer hair cells (OHCs).
* **The 4kHz Notch:** Due to the natural resonance of the human ear canal, blast energy is heavily concentrated between 3,000 Hz and 6,000 Hz, creating a distinct "notch" of hearing loss in this range.
* **Hidden Hearing Loss:** BIHL often causes Cochlear Synaptopathy, degrading the synapses between hair cells and the auditory nerve, which severely impairs speech-in-noise perception even if standard audiograms appear normal. Blasts also cause deficits in Extended High Frequencies (9-16 kHz).

## 3. Proposed Architecture & Mechanism of Action
The core architecture of the Smart Strap moves away from traditional acoustic amplification and relies entirely on Sensory Substitution and Neuroplasticity.

* **Haptic Translation:** Acoustic information that the damaged cochlea can no longer process is translated into tactile vibrations delivered directly to the user's skin.
* **Cross-Modal Plasticity:** By leveraging Hebbian learning ("Neurons that fire together, wire together"), the auditory cortex is recruited to process these tactile stimuli, allowing the user's brain to eventually interpret the vibrations as meaningful sound.
* **Bimodal Neuromodulation:** To treat tinnitus, the device delivers a tactile anchor synchronized with ambient sound. This bimodal stimulation aims to reduce the "neural hunger" caused by the 4kHz notch and reset the hyperactive neural firing responsible for the ringing.

## 4. System Design Principles
The device is engineered around three foundational pillars that separate it from conventional hearing aids:

* **Audiogram-Based Selective Feedback:** The system is personally calibrated to trigger haptic feedback only at the specific frequencies where the user has a measured deficit (e.g., the 4kHz notch). This precision prevents the sensory overload commonly caused by traditional hearing aids that uniformly amplify all sounds.
* **Discreet Integration:** The haptic actuators are embedded within a standard, everyday watch strap. This invisible design ensures social normalization and mitigates the stigma associated with prominent medical assistive devices.
* **Therapeutic Functionality:** Beyond serving as a sensory substitution tool for hearing, the bimodal stimulation specifically targets and modulates post-traumatic tinnitus, acting as a direct therapeutic intervention.

## 5. Market Positioning & Future Direction
Current conventional hearing aids uniformly amplify the audio spectrum, which introduces unnecessary noise and severe cognitive overload for blast-injured patients who hear most frequencies normally.

Previous haptic market attempts, such as the Neosensory Buzz, provided a successful proof of concept for sensory substitution using an array of four vibratory motors. However, they suffered from critical design gaps. The Buzz utilized a prominent silicone wristband leading to "over-instrumentation," and relied on generic broadband frequency translation that created exhausting sensory noise for the user.

The Smart Strap aims to fill the current market vacuum by offering a highly personalized alternative. By operating exclusively where a proven audiometric gap exists and integrating into a daily accessory, the project targets higher long-term user compliance and a significantly cleaner sensory experience.
