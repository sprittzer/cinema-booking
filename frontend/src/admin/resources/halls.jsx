import {
  Box,
  Button,
  CircularProgress,
  Divider,
  TextField as MuiTextField,
  Paper,
  Stack,
  Tooltip,
  Typography,
} from "@mui/material";
import { useEffect, useState } from "react";
import { Datagrid, List, NumberField, Show, TextField, useNotify, useRedirect, useShowContext } from "react-admin";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const SEAT_TYPES = ["standard", "vip", "couple", "inactive"];
const SEAT_CYCLE = { standard: "vip", vip: "couple", couple: "inactive", inactive: "standard" };

const SEAT_STYLE = {
  standard: { bg: "#78909c", label: "Стандарт" },
  vip: { bg: "#ffc107", label: "VIP" },
  couple: { bg: "#ec407a", label: "Пара" },
  inactive: { bg: "#37474f", label: "Нет места" },
};

function SeatMap({ rows, cols, seats, onToggle }) {
  const getSeat = (row, num) => seats.find((s) => s.row === row && s.number === num);

  return (
    <Box sx={{ overflowX: "auto", py: 1 }}>
      <Box
        sx={{
          width: Math.min(cols * 32, 700),
          minWidth: 200,
          mx: "auto",
          bgcolor: "grey.800",
          color: "white",
          textAlign: "center",
          py: 0.5,
          borderRadius: "6px 6px 0 0",
          fontSize: 12,
          letterSpacing: 4,
          mb: 2,
        }}
      >
        ЭКРАН
      </Box>

      <Stack spacing={0.5} alignItems="center">
        {Array.from({ length: rows }, (_, ri) => {
          const row = ri + 1;
          return (
            <Box key={row} sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
              <Typography variant="caption" sx={{ width: 18, textAlign: "right", color: "text.secondary", mr: 0.5 }}>
                {row}
              </Typography>
              {Array.from({ length: cols }, (_, ci) => {
                const num = ci + 1;
                const seat = getSeat(row, num);
                const type = seat?.seat_type ?? "standard";
                return (
                  <Tooltip key={num} title={`Р${row} М${num} — ${SEAT_STYLE[type].label}`} placement="top">
                    <Box
                      onClick={() => onToggle(row, num)}
                      sx={{
                        width: 26,
                        height: 22,
                        borderRadius: "4px 4px 2px 2px",
                        bgcolor: SEAT_STYLE[type].bg,
                        cursor: "pointer",
                        transition: "opacity 0.15s",
                        "&:hover": { opacity: 0.75 },
                        flexShrink: 0,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: 13,
                        color: "rgba(255,255,255,0.7)",
                        fontWeight: "bold",
                      }}
                    >
                      {type === "inactive" ? "×" : null}
                    </Box>
                  </Tooltip>
                );
              })}
              <Typography variant="caption" sx={{ width: 18, textAlign: "left", color: "text.secondary", ml: 0.5 }}>
                {row}
              </Typography>
            </Box>
          );
        })}
      </Stack>

      <Stack direction="row" spacing={2} justifyContent="center" mt={3}>
        {SEAT_TYPES.map((type) => (
          <Stack key={type} direction="row" alignItems="center" spacing={0.5}>
            <Box sx={{ width: 18, height: 16, borderRadius: "3px 3px 1px 1px", bgcolor: SEAT_STYLE[type].bg }} />
            <Typography variant="caption">{SEAT_STYLE[type].label}</Typography>
          </Stack>
        ))}
        <Typography variant="caption" color="text.secondary">· клик меняет тип</Typography>
      </Stack>
    </Box>
  );
}

function initSeats(rows, cols) {
  const result = [];
  for (let r = 1; r <= rows; r++) {
    for (let n = 1; n <= cols; n++) {
      result.push({ row: r, number: n, seat_type: "standard", is_active: true });
    }
  }
  return result;
}

export function HallCreate() {
  const [step, setStep] = useState("config");
  const [name, setName] = useState("");
  const [rows, setRows] = useState(8);
  const [cols, setCols] = useState(15);
  const [seats, setSeats] = useState([]);
  const [saving, setSaving] = useState(false);

  const notify = useNotify();
  const redirect = useRedirect();

  const handleGenerate = () => {
    if (!name.trim()) return notify("Введите название зала", { type: "warning" });
    if (rows < 1 || cols < 1) return notify("Некорректные размеры", { type: "warning" });
    setSeats(initSeats(rows, cols));
    setStep("layout");
  };

  const handleToggle = (row, num) => {
    setSeats((prev) =>
      prev.map((s) => {
        if (s.row !== row || s.number !== num) return s;
        const next = SEAT_CYCLE[s.seat_type];
        return { ...s, seat_type: next, is_active: next !== "inactive" };
      })
    );
  };

  const handleSave = async () => {
    setSaving(true);
    const token = localStorage.getItem("admin_token");
    try {
      const hallRes = await fetch(`${API_URL}/halls`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ name, rows, seats_per_row: cols }),
      });
      if (!hallRes.ok) {
        const err = await hallRes.json();
        throw new Error(err.detail || "Ошибка создания зала");
      }
      const hall = await hallRes.json();

      const seatsRes = await fetch(`${API_URL}/halls/${hall.id}/seats`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const createdSeats = await seatsRes.json();

      const needsUpdate = seats.filter((s) => s.seat_type !== "standard" || !s.is_active);
      await Promise.all(
        needsUpdate.map((s) => {
          const created = createdSeats.find((cs) => cs.row === s.row && cs.number === s.number);
          if (!created) return Promise.resolve();
          const body =
            s.seat_type === "inactive"
              ? { is_active: false }
              : { seat_type: s.seat_type };
          return fetch(`${API_URL}/halls/${hall.id}/seats/${created.id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
            body: JSON.stringify(body),
          });
        })
      );

      notify("Зал создан", { type: "success" });
      redirect("list", "halls");
    } catch (e) {
      notify(e.message || "Ошибка", { type: "error" });
    } finally {
      setSaving(false);
    }
  };

  return (
    <Paper sx={{ maxWidth: 860, mx: "auto", mt: 3, p: 3 }}>
      <Typography variant="h6" gutterBottom>
        {step === "config" ? "Новый зал" : `Зал «${name}» — настройка мест`}
      </Typography>
      <Divider sx={{ mb: 3 }} />

      {step === "config" ? (
        <Stack spacing={2} maxWidth={360}>
          <MuiTextField
            label="Название зала"
            value={name}
            onChange={(e) => setName(e.target.value)}
            fullWidth
            required
          />
          <MuiTextField
            label="Количество рядов"
            type="number"
            value={rows}
            onChange={(e) => setRows(Math.max(1, Number(e.target.value)))}
            inputProps={{ min: 1, max: 30 }}
          />
          <MuiTextField
            label="Мест в ряду"
            type="number"
            value={cols}
            onChange={(e) => setCols(Math.max(1, Number(e.target.value)))}
            inputProps={{ min: 1, max: 50 }}
          />
          <Button variant="contained" onClick={handleGenerate}>
            Сгенерировать план →
          </Button>
        </Stack>
      ) : (
        <>
          <SeatMap rows={rows} cols={cols} seats={seats} onToggle={handleToggle} />
          <Divider sx={{ my: 3 }} />
          <Stack direction="row" spacing={2}>
            <Button variant="outlined" onClick={() => setStep("config")}>
              ← Назад
            </Button>
            <Button variant="contained" onClick={handleSave} disabled={saving}>
              {saving ? <CircularProgress size={18} sx={{ mr: 1 }} /> : null}
              Сохранить зал
            </Button>
          </Stack>
        </>
      )}
    </Paper>
  );
}

function HallShowLayout() {
  const { record } = useShowContext();
  const [seats, setSeats] = useState([]);
  const [saving, setSaving] = useState(false);
  const notify = useNotify();
  const token = localStorage.getItem("admin_token");

  useEffect(() => {
    if (!record?.id) return;
    fetch(`${API_URL}/halls/${record.id}/seats`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then(setSeats)
      .catch(() => {});
  }, [record?.id]);

  const handleToggle = (row, num) => {
    setSeats((prev) =>
      prev.map((s) => {
        if (s.row !== row || s.number !== num) return s;
        const next = SEAT_CYCLE[s.seat_type];
        return { ...s, seat_type: next, is_active: next !== "inactive" };
      })
    );
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const origRes = await fetch(`${API_URL}/halls/${record.id}/seats`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const origSeats = await origRes.json();
      await Promise.all(
        seats.map((s) => {
          const orig = origSeats.find((os) => os.id === s.id);
          if (!orig || (orig.seat_type === s.seat_type && orig.is_active === s.is_active))
            return Promise.resolve();
          const body =
            s.seat_type === "inactive" ? { is_active: false } : { seat_type: s.seat_type, is_active: true };
          return fetch(`${API_URL}/halls/${record.id}/seats/${s.id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
            body: JSON.stringify(body),
          });
        })
      );
      notify("Изменения сохранены", { type: "success" });
    } catch {
      notify("Ошибка сохранения", { type: "error" });
    } finally {
      setSaving(false);
    }
  };

  if (!record) return null;

  return (
    <Paper sx={{ maxWidth: 860, mx: "auto", mt: 3, p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Зал «{record.name}» — {record.rows} рядов × {record.seats_per_row} мест
      </Typography>
      <Divider sx={{ mb: 3 }} />
      <SeatMap rows={record.rows} cols={record.seats_per_row} seats={seats} onToggle={handleToggle} />
      <Divider sx={{ my: 3 }} />
      <Stack direction="row" spacing={2}>
        <Button variant="contained" onClick={handleSave} disabled={saving}>
          {saving ? <CircularProgress size={18} sx={{ mr: 1 }} /> : null}
          Сохранить изменения
        </Button>
      </Stack>
    </Paper>
  );
}

export function HallShow() {
  return (
    <Show>
      <HallShowLayout />
    </Show>
  );
}

export const HallList = () => (
  <List>
    <Datagrid rowClick="show">
      <NumberField source="id" label="ID" />
      <TextField source="name" label="Название" />
      <NumberField source="rows" label="Рядов" />
      <NumberField source="seats_per_row" label="Мест в ряду" />
    </Datagrid>
  </List>
);
