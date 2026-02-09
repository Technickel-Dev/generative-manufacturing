import { useState } from "react";
import styles from "./ShiftBrief.module.css";

export function ShiftBrief() {
    const [isMinimized, setIsMinimized] = useState(false);

    return (
        <div
            className={`${styles.panel} ${isMinimized ? styles.minimized : ''}`}
            onClick={(_e) => {
                // Allow clicking anywhere on the minimized panel to expand it
                if (isMinimized) setIsMinimized(false);
            }}
        >
            <div className={styles.header}>
                <div className={styles.title}>
                    <span>📋 Shift Brief</span>
                </div>
                <button
                    className={styles.toggleButton}
                    onClick={(e) => {
                        e.stopPropagation();
                        setIsMinimized(!isMinimized);
                    }}
                    title={isMinimized ? "Expand" : "Minimize"}
                >
                    {isMinimized ? "➕" : "➖"}
                </button>
            </div>

            <div className={styles.content}>
                <div className={styles.section}>
                    <span className={styles.label}>Shift Objective</span>
                    <div>
                        The original vision was to create a fully immersive chat and app experience that you might find in a high-tech factory environment to showcase generative manufacturing in its entirety. However, due to time constraints for writing my own client from scratch and limited support for the MCP Apps Extension in most host applications, we have streamlined this "demo-host" to focus on the core tool calling capabilities.
                    </div>
                </div>

                <div className={`${styles.section} ${styles.warning}`}>
                    <span className={styles.label}>Security Protocol</span>
                    <div>
                        Please note that all physical printer interactions in this demo are <strong>MOCKED</strong>. This is a deliberate security measure. as my parents always told me, <em>"Never let strangers into your house"</em>—and that applies to my home network and 3D printer too!
                        <br /><br />
                        However, the Gemini 3 functionality driving this demo is <strong>LIVE</strong>
                    </div>
                </div>
            </div>
        </div>
    );
}
