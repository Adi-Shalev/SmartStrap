# Project Charter: Smart Strap
**Author:** Adi Shalev  
**Domain:** Biomedical Engineering, Afeka College  

## 1. Project Overview & Objective
This project centers on the development of a smart watch strap utilizing Targeted Frequency Mapping technology. The primary objective is to engineer a personalized haptic wearable device that addresses the unique pathophysiological needs of individuals suffering from Blast-Induced Hearing Loss (BIHL) or any specific frequency-band hearing deficit. By expanding the target audience beyond military personnel to all blast and acoustic trauma survivors, the project offers a universal, non-invasive rehabilitative solution.

## 2. Clinical Background & The Problem
Unlike continuous noise exposure, blast waves create a high-pressure shockwave that inflicts dual-impact damage to the ear:
*   **Mechanical and Sensorineural Damage:** The overpressure can rupture the tympanic membrane and violently displace the basilar membrane, leading to the destruction of outer hair cells (OHCs).
*   **The 4kHz Notch:** Due to the natural resonance of the human ear canal, blast energy is heavily concentrated between 3,000 Hz and 6,000 Hz, creating a distinct "notch" of hearing loss in this range.
*   **Hidden Hearing Loss:** BIHL often causes Cochlear Synaptopathy, degrading the synapses between hair cells and the auditory nerve, which severely impairs speech-in-noise perception even if standard audiograms appear normal.

## 3. Proposed Architecture & Mechanism of Action
The core architecture of the Smart Strap moves away from traditional acoustic amplification and relies on Sensory Substitution and Neuroplasticity:
*   **Haptic Translation:** Acoustic information that the damaged cochlea can no longer process is translated into tactile vibrations delivered directly to the user's skin.
*   **Cross-Modal Plasticity & Active Training Mode:** To accelerate brain adaptation (leveraging Hebbian learning), the system features a dedicated **Training Mode**. In this environment, the user selects a track from a predefined music playlist. As the song plays and is visualized on the UI, the device triggers synchronized haptic vibrations and screen flashes specifically when the user's missing frequencies occur. This multi-sensory integration (audio, visual, and tactile) actively trains the auditory cortex to interpret vibrations as meaningful sound.
*   **Bimodal Neuromodulation:** To treat accompanying tinnitus, the device delivers a tactile anchor synchronized with ambient sound, aiming to reduce the "neural hunger" caused by the 4kHz notch and reset hyperactive neural firing.

## 4. System Design Principles
*   **Audiogram-Based Selective Feedback:** The system is personally calibrated to trigger haptic feedback *only* at the specific frequencies where the user has a measured deficit. This precision prevents the sensory overload commonly caused by traditional hearing aids.
*   **Open-Source Algorithmic Baseline:** The development of the audio-to-haptic algorithm will not start from scratch. The project will leverage existing open-source industrial repositories (such as Neosensory's GitHub SDKs) as an engineering baseline. We will analyze their generic translation methods and modify the architecture to create a highly targeted filter that extracts only the patient-specific missing frequencies.
*   **Discreet Integration:** The haptic actuators are embedded within a standard everyday watch strap, ensuring social normalization and mitigating medical stigma.

## 5. Development Roadmap & Phased Architecture
The system architecture is strictly modular and phased to allow safe development from a software baseline to an independent wearable:
*   **Phase 1: Software-Only PoC (Current Focus):** Developed for the immediate programming course requirements. The system runs entirely on a PC environment with no physical hardware integration. Focus is on establishing the Front-end GUI, the database (MySQL), and simulating the audio processing and frequency detection algorithms within Python.
*   **Phase 2: Tethered Hardware Prototype (Capstone Project):** Integration between the PC software and physical hardware. The PC will handle the heavy signal processing and transmit operational commands to a tethered microcontroller (e.g., Arduino), which will drive the physical vibration motors to prove haptic viability.
*   **Phase 3: Wireless Edge Device (Future Commercialization):** Post-degree development. Processing capabilities will migrate fully to edge hardware. The strap will act as a standalone, Bluetooth-enabled wearable device connected to a smartwatch, functioning autonomously in daily life.

## 6. Market Positioning & Future Direction
Current conventional hearing aids uniformly amplify the audio spectrum, introducing unnecessary noise and cognitive overload for blast-injured patients who hear most frequencies normally. Previous haptic attempts (e.g., Neosensory Buzz) provided a proof of concept but suffered from "over-instrumentation" and generic broadband translation that created exhausting sensory noise. The Smart Strap fills this market vacuum by offering a highly personalized, targeted-frequency alternative integrated into a daily accessory, ensuring a cleaner sensory experience and higher long-term compliance.