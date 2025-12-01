# Simulatore di packing
# - 3 tipologie: Cuffie Bluetooth, Tablet, Stampante
# - 5 fasi: Picking, Qualità, Imballaggio, Etichettatura, Smistamento
# - Pipeline con code per fase × tipologia + worker (thread)
# - KPI stampati a fine run (tempo simulato)
# - Export locale opzionale in JSON + TXT per analisi offline
# - Opzionale: pandas/matplotlib per piccola analisi/grafici (se installati)

import threading
import queue
import time
import random
import json
import os
from datetime import datetime
from statistics import mean

# Opzionali (se non presenti, lo script funziona lo stesso)
try:
    import pandas as pd
    HAS_PANDAS = True
except Exception:
    HAS_PANDAS = False

try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except Exception:
    HAS_MPL = False


class CentroPacking:
    def __init__(self, time_scale=1.0, seed=42):
        random.seed(seed)

        # Tipologie e fasi
        self.tipologia = ["Cuffie Bluetooth", "Tablet", "Stampante"]
        self.fasi = ["Picking", "Qualità", "Imballaggio", "Etichettatura", "Smistamento"]

        # Code per tipologia × fase
        self.code = {tipo: [queue.Queue() for _ in range(len(self.fasi))] for tipo in self.tipologia}

        # Parametri e stato
        self.parametri = {"tempi": {}, "prob_rework": 0.0}
        self._lock = threading.Lock()

        # Tempi simulati di ingresso/uscita e tempo corrente per ordine
        self.start_ts = {}           # ordine_id -> tempo simulato di inizio
        self.end_ts = {}             # ordine_id -> tempo simulato di fine
        self.current_sim_time = {}   # ordine_id -> tempo simulato corrente

        # Tempo di disponibilità del server per fase × tipologia (tempo simulato)
        self.server_next_free = {
            tipo: [0.0 for _ in range(len(self.fasi))]
            for tipo in self.tipologia
        }

        # Fattore velocità (sleep = tempo_simulato * time_scale) per demo rapide
        self.time_scale = max(0.0, float(time_scale))

        # Per report
        self.demo_params = {
            "range_ordini": None,
            "range_tempo": None,
            "prob_rework": None,
            "time_scale": self.time_scale,
        }

        # Tempo reale di esecuzione dell'ultima run (solo informativo)
        self.runtime_sec = 0.0

    # -----------------------------
    # Parametri e ordini
    # -----------------------------
    def genera_parametri(self, range_tempo, prob_rework):
        lo, hi = range_tempo
        if lo < 0 or hi < 0 or lo > hi:
            raise ValueError("Range tempi non valido (usa min <= max e valori >= 0).")
        if not (0.0 <= prob_rework <= 1.0):
            raise ValueError("La probabilità di rework deve essere tra 0 e 1.")
        # Un tempo base (in secondi simulati) per ciascuna fase × tipologia
        for tipo in self.tipologia:
            self.parametri["tempi"][tipo] = [random.randint(lo, hi) for _ in self.fasi]
        self.parametri["prob_rework"] = prob_rework
        print("→ Parametri generati.")

    def genera_ordini(self, range_ordini):
        lo, hi = range_ordini
        if lo < 0 or hi < 0 or lo > hi:
            raise ValueError("Range ordini non valido (usa min <= max e valori >= 0).")
        for tipo in self.tipologia:
            n = random.randint(lo, hi)
            for i in range(n):
                oid = f"{tipo}-{i:04d}"
                # Tutti gli ordini entrano nel reparto a tempo simulato 0
                with self._lock:
                    self.start_ts[oid] = 0.0
                    self.current_sim_time[oid] = 0.0
                self.code[tipo][0].put(oid)
        print("→ Ordini generati.")

    # -----------------------------
    # Worker di fase
    # -----------------------------
    def lavorazione_fase(self, tipo, fase_index, range_tempo):
        while True:
            ordine = self.code[tipo][fase_index].get()
            base = self.parametri["tempi"][tipo][fase_index]
            fase_nome = self.fasi[fase_index]

            # Durata di lavorazione simulata = tempo base + eventuale rework
            extra = 0
            if random.random() < self.parametri["prob_rework"]:
                extra = random.randint(range_tempo[0], range_tempo[1])
            durata_sim = base + extra

            # Aggiornamento del tempo simulato (gestione coda + server)
            with self._lock:
                arr = self.current_sim_time.get(ordine, 0.0)
                server_free = self.server_next_free[tipo][fase_index]
                start_sim = max(arr, server_free)
                end_sim = start_sim + durata_sim
                self.server_next_free[tipo][fase_index] = end_sim
                self.current_sim_time[ordine] = end_sim
                if fase_index == 0 and ordine not in self.start_ts:
                    self.start_ts[ordine] = start_sim
                if fase_index == len(self.fasi) - 1:
                    self.end_ts[ordine] = end_sim

            print(f"{ordine}: fase {fase_nome} in corso ({durata_sim}s simulati)...")
            if extra > 0:
                print(f"{ordine}: REWORK su {fase_nome} (+{extra}s simulati).")

            # Sleep solo per visualizzazione (non influisce sui tempi simulati)
            if self.time_scale > 0 and durata_sim > 0:
                time.sleep(durata_sim * self.time_scale)

            print(f"{ordine}: fase {fase_nome} completata (t_sim={end_sim:.2f}s).")

            # Passaggio alla fase successiva / Fine
            if fase_index < len(self.fasi) - 1:
                self.code[tipo][fase_index + 1].put(ordine)
            self.code[tipo][fase_index].task_done()

    # -----------------------------
    # Avvio simulazione
    # -----------------------------
    def avvio_produzione(self, range_ordini, range_tempo, prob_rework):
        print("Simulatore reparto di packing (settore elettronico)\n")
        self.demo_params.update({
            "range_ordini": list(range_ordini),
            "range_tempo": list(range_tempo),
            "prob_rework": prob_rework,
            "time_scale": self.time_scale,
        })

        real_t0 = time.time()

        self.genera_parametri(range_tempo, prob_rework)
        self.genera_ordini(range_ordini)

        # Avvio worker (uno per tipologia × fase)
        for tipo in self.tipologia:
            for idx in range(len(self.fasi)):
                threading.Thread(
                    target=self.lavorazione_fase, args=(tipo, idx, range_tempo),
                    daemon=True
                ).start()

        # Attendo svuotamento code
        for tipo in self.tipologia:
            for idx in range(len(self.fasi)):
                self.code[tipo][idx].join()

        real_t1 = time.time()
        self.runtime_sec = real_t1 - real_t0

        # Makespan calcolato sul TEMPO SIMULATO (non sul tempo reale)
        if self.end_ts:
            makespan_sim = max(self.end_ts.values()) - min(self.start_ts.values())
        else:
            makespan_sim = 0.0

        print(f"\n✅ Packing lotto completato.")
        print(f" - Makespan simulato: {makespan_sim:.2f} s")
        print(f" - Tempo reale di esecuzione: {self.runtime_sec:.2f} s")
        return makespan_sim

    # -----------------------------
    # KPI (tempo simulato)
    # -----------------------------
    def compute_kpis(self, ultimi=20):
        completati = [oid for oid in self.end_ts.keys() if oid in self.start_ts]
        if not completati:
            return {
                "orders_completed": 0,
                "lead_time_avg_sec": 0.0,
                "lead_time_med_sec": 0.0,
                "lead_time_avg_by_type": {},
                "last_completed": [],
            }

        lts = []
        per_tipo = {t: [] for t in self.tipologia}
        for oid in completati:
            lt = self.end_ts[oid] - self.start_ts[oid]
            lts.append(lt)
            t = oid.rsplit("-", 1)[0]
            if t in per_tipo:
                per_tipo[t].append(lt)

        # Ultimi N completati (in base al tempo simulato di fine)
        ultimi_ids = sorted(completati, key=lambda k: self.end_ts[k])[-ultimi:]
        last_rows = []
        for oid in ultimi_ids:
            end_sim = self.end_ts[oid]
            lt = self.end_ts[oid] - self.start_ts[oid]
            last_rows.append({
                "order_id": oid,
                "ended_at_sim_sec": round(end_sim, 3),
                "lead_time_sec": round(lt, 3),
            })

        return {
            "orders_completed": len(completati),
            "lead_time_avg_sec": round(mean(lts), 3),
            "lead_time_med_sec": round(sorted(lts)[len(lts) // 2], 3),
            "lead_time_avg_by_type": {
                t: (round(mean(a), 3) if a else 0.0) for t, a in per_tipo.items()
            },
            "last_completed": last_rows,
        }

    def stampa_kpi(self, ultimi=20):
        kpi = self.compute_kpis(ultimi)
        if kpi["orders_completed"] == 0:
            print("\n[Nessun ordine completato: impossibile calcolare KPI]")
            return
        print("\n--- KPI (tempo simulato) ---")
        print(f"Ordini completati: {kpi['orders_completed']}")
        print(f"Lead time medio: {kpi['lead_time_avg_sec']:.2f}s")
        print(f"Lead time mediano: {kpi['lead_time_med_sec']:.2f}s")
        for t, v in kpi["lead_time_avg_by_type"].items():
            print(f"- {t}: lead time medio {v:.2f}s")
        print("\nUltimi completati (tempo simulato):")
        print(f"{'FINE_SIM(s)':<15} {'ORDINE':<26} {'LEAD_TIME(s)':>12}")
        print("-" * 60)
        for row in kpi["last_completed"]:
            print(
                f"{row['ended_at_sim_sec']:<15.2f} "
                f"{row['order_id']:<26} {row['lead_time_sec']:>12.2f}"
            )

    # -----------------------------
    # Dati per analisi/export
    # -----------------------------
    def build_order_records(self):
        """Crea una lista di record per ordine: id, type, start/end in tempo simulato, lead_time_sec."""
        recs = []
        for oid, end_sim in self.end_ts.items():
            if oid not in self.start_ts:
                continue
            start_sim = self.start_ts[oid]
            lt = end_sim - start_sim
            tipo = oid.rsplit("-", 1)[0]
            recs.append({
                "order_id": oid,
                "type": tipo,
                "start_sim_sec": round(start_sim, 3),
                "end_sim_sec": round(end_sim, 3),
                "lead_time_sec": round(lt, 3),
            })
        return recs

    def build_export_payload(self, makespan_sec, ultimi=20, include_orders=True):
        """Payload JSON leggibile per analisi offline (tempo simulato)."""
        kpi = self.compute_kpis(ultimi=ultimi)
        payload = {
            "generated_at_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "params": self.demo_params,
            "kpis": kpi,
            "makespan_sec": round(makespan_sec, 3),          # makespan sul tempo simulato
            "runtime_real_sec": round(self.runtime_sec, 3),  # tempo reale di esecuzione
        }
        if include_orders:
            payload["orders"] = self.build_order_records()
        # Versione TXT “umana”
        lines = []
        lines.append("=== Simulatore di Packing - Report ===")
        lines.append(f"Generato UTC: {payload['generated_at_utc']}")
        lines.append(f"Parametri: {json.dumps(self.demo_params)}")
        lines.append(f"Ordini completati: {kpi['orders_completed']}")
        lines.append(f"Lead time medio (sim): {kpi['lead_time_avg_sec']} s")
        lines.append(f"Lead time mediano (sim): {kpi['lead_time_med_sec']} s")
        lines.append(f"Lead time medio per tipologia (sim): {json.dumps(kpi['lead_time_avg_by_type'])}")
        lines.append(f"Makespan simulato: {payload['makespan_sec']} s")
        lines.append(f"Tempo reale di esecuzione: {payload['runtime_real_sec']} s")
        lines.append("Ultimi completati (tempo simulato):")
        for row in kpi["last_completed"]:
            lines.append(f" - t_sim={row['ended_at_sim_sec']}s  {row['order_id']}  {row['lead_time_sec']}s")
        txt = "\n".join(lines)
        return payload, txt

    def save_report_files(self, out_dir, prefix, payload_json, report_txt):
        """Scrive JSON e TXT su disco, restituendo i percorsi."""
        os.makedirs(out_dir, exist_ok=True)
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        json_path = os.path.join(out_dir, f"{prefix}_{ts}.json")
        txt_path  = os.path.join(out_dir, f"{prefix}_{ts}.txt")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(payload_json, f, ensure_ascii=False, indent=2)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(report_txt)
        return {"json": json_path, "txt": txt_path}

    # -----------------------------
    # Analisi/plot opzionali
    # -----------------------------
    def to_dataframe(self):
        if not HAS_PANDAS:
            print("Pandas non disponibile (pip install pandas).")
            return None
        return pd.DataFrame(self.build_order_records())

    def plot_summary(self):
        if not (HAS_PANDAS and HAS_MPL):
            print("Per i grafici servono pandas e matplotlib (pip install pandas matplotlib).")
            return
        df = self.to_dataframe()
        if df is None or df.empty:
            print("Nessun dato per i grafici.")
            return
        # Lead time medio per tipologia
        plt.figure()
        df.groupby("type")["lead_time_sec"].mean().sort_values().plot(kind="bar")
        plt.title("Lead time medio per tipologia (s, tempo simulato)")
        plt.ylabel("secondi"); plt.xlabel("tipologia"); plt.tight_layout(); plt.show()
        # Istogramma dei lead time
        plt.figure()
        df["lead_time_sec"].plot(kind="hist", bins=20)
        plt.title("Distribuzione lead time (tempo simulato, s)")
        plt.xlabel("secondi"); plt.tight_layout(); plt.show()


# -----------------------------
# Input interattivo e run
# -----------------------------
def _ask_int(prompt, default, min_val=0):
    s = input(f"{prompt} [{default}]: ").strip()
    if not s:
        return default
    v = int(s)
    if v < min_val:
        raise ValueError(f"Valore minimo {min_val}.")
    return v

def _ask_float(prompt, default, min_val=0.0, max_val=1.0):
    s = input(f"{prompt} [{default}]: ").strip()
    if not s:
        return default
    v = float(s)
    if v < min_val or v > max_val:
        raise ValueError(f"Inserisci un valore tra {min_val} e {max_val}.")
    return v


if __name__ == "__main__":
    print("\n===============================")
    print("  Simulatore reparto di packing (settore elettronico)")
    print("===============================\n")

    print("=== Simulazione Packing (export JSON/TXT opzionale) ===")
    print("Premi INVIO per usare i default tra parentesi.\n")

    try:
        ord_min = _ask_int("Numero MIN per tipologia (ordini)", 10, 0)
        ord_max = _ask_int("Numero MAX per tipologia (ordini)", 20, ord_min)
        tmp_min = _ask_int("Tempo MIN per fase (secondi simulati)", 5, 0)
        tmp_max = _ask_int("Tempo MAX per fase (secondi simulati)", 12, tmp_min)
        p_rw    = _ask_float("Probabilità REWORK (0–1)", 0.05, 0.0, 1.0)
        tscale  = _ask_float("Fattore velocità sleep (es. 0.05=20× più veloce)", 0.05, 0.0, 10.0)

        sim = CentroPacking(time_scale=tscale, seed=42)
        makespan_sim = sim.avvio_produzione(
            range_ordini=(ord_min, ord_max),
            range_tempo=(tmp_min, tmp_max),
            prob_rework=p_rw
        )
        sim.stampa_kpi(ultimi=20)

        # Analisi/plot opzionali
        if HAS_PANDAS and HAS_MPL:
            show = input("\nMostrare grafici con pandas/matplotlib? (s/N): ").strip().lower()
            if show == "s":
                sim.plot_summary()

        # Export locale JSON/TXT
        exp = input("\nEsportare report su file (JSON + TXT)? (s/N): ").strip().lower()
        if exp == "s":
            out_dir = input("  Cartella di output [output]: ").strip() or "output"
            prefix  = input("  Prefisso file     [packing_report]: ").strip() or "packing_report"
            payload, txt = sim.build_export_payload(makespan_sec=makespan_sim, ultimi=20, include_orders=True)
            paths = sim.save_report_files(out_dir, prefix, payload, txt)
            print("\nReport salvati:")
            print(" - JSON:", paths["json"])
            print(" - TXT :", paths["txt"])

    except Exception as e:
        print("Errore:", e)
