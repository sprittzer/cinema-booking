import SearchIcon from "@mui/icons-material/Search";
import {
  Box,
  CircularProgress,
  InputAdornment,
  ListItemButton,
  TextField as MuiTextField,
  Typography,
} from "@mui/material";
import { useEffect, useState } from "react";
import {
  BooleanField,
  BooleanInput,
  Create,
  Datagrid,
  Edit,
  List,
  NumberField,
  NumberInput,
  SelectField,
  SelectInput,
  SimpleForm,
  TextField,
  TextInput,
  useNotify,
  useRedirect,
} from "react-admin";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const GENRE_CHOICES = [
  { id: "action", name: "Боевик" },
  { id: "drama", name: "Драма" },
  { id: "comedy", name: "Комедия" },
  { id: "horror", name: "Ужасы" },
  { id: "sci_fi", name: "Фантастика" },
  { id: "thriller", name: "Триллер" },
  { id: "romance", name: "Романтика" },
  { id: "animation", name: "Анимация" },
  { id: "documentary", name: "Документальный" },
  { id: "other", name: "Другое" },
];

const AGE_CHOICES = [
  { id: "0+", name: "0+" },
  { id: "6+", name: "6+" },
  { id: "12+", name: "12+" },
  { id: "16+", name: "16+" },
  { id: "18+", name: "18+" },
];

const STATUS_CHOICES = [
  { id: "now_playing", name: "В прокате" },
  { id: "coming_soon", name: "Скоро" },
  { id: "archived", name: "Архив" },
];

const MovieFormFields = () => (
  <>
    <TextInput source="title" label="Название" required fullWidth />
    <TextInput source="description" label="Описание" multiline rows={4} fullWidth />
    <NumberInput source="duration" label="Длительность (мин)" />
    <SelectInput source="genre" label="Жанр" choices={GENRE_CHOICES} />
    <SelectInput source="age_limit" label="Возрастной рейтинг" choices={AGE_CHOICES} />
    <SelectInput source="status" label="Статус" choices={STATUS_CHOICES} defaultValue="now_playing" />
    <TextInput source="poster_url" label="URL постера" fullWidth />
    <TextInput source="trailer_url" label="URL трейлера" fullWidth />
    <BooleanInput source="is_featured" label="Главный фильм" />
  </>
);

function TMDBSearch({ onManual }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [importing, setImporting] = useState(null);
  const notify = useNotify();
  const redirect = useRedirect();

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      setSearching(true);
      try {
        const res = await fetch(
          `${API_URL}/movies/search/tmdb?query=${encodeURIComponent(query)}`,
          { headers: { Authorization: `Bearer ${localStorage.getItem("admin_token")}` } }
        );
        if (!res.ok) throw new Error();
        setResults(await res.json());
      } catch {
        notify("Ошибка поиска TMDB", { type: "error" });
      } finally {
        setSearching(false);
      }
    }, 400);
    return () => clearTimeout(timer);
  }, [query, notify]);

  const handleImport = async (tmdbId) => {
    setImporting(tmdbId);
    try {
      const res = await fetch(`${API_URL}/movies/import/tmdb`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("admin_token")}`,
        },
        body: JSON.stringify({ tmdb_id: tmdbId }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Ошибка импорта");
      notify("Фильм импортирован", { type: "success" });
      redirect("list", "movies");
    } catch (e) {
      notify(e.message, { type: "error" });
    } finally {
      setImporting(null);
    }
  };

  return (
    <Box sx={{ maxWidth: 560, p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Импорт из TMDB
      </Typography>

      <MuiTextField
        fullWidth
        placeholder="Начните вводить название фильма..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        autoFocus
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              {searching ? <CircularProgress size={18} /> : <SearchIcon />}
            </InputAdornment>
          ),
        }}
        sx={{ mb: 1 }}
      />

      <Box sx={{ border: results.length ? "1px solid" : "none", borderColor: "divider", borderRadius: 1 }}>
        {results.map((r, i) => (
          <ListItemButton
            key={r.tmdb_id}
            onClick={() => handleImport(r.tmdb_id)}
            disabled={importing !== null}
            divider={i < results.length - 1}
            sx={{ gap: 2, alignItems: "flex-start", py: 1 }}
          >
            {r.poster_url ? (
              <Box
                component="img"
                src={r.poster_url}
                sx={{ width: 46, height: 68, objectFit: "cover", borderRadius: 0.5, flexShrink: 0 }}
              />
            ) : (
              <Box sx={{ width: 46, height: 68, bgcolor: "grey.200", borderRadius: 0.5, flexShrink: 0 }} />
            )}
            <Box sx={{ flex: 1 }}>
              <Typography variant="body1" fontWeight={500}>
                {r.title}
              </Typography>
              {r.year && (
                <Typography variant="body2" color="text.secondary">
                  {r.year}
                </Typography>
              )}
            </Box>
            {importing === r.tmdb_id && <CircularProgress size={18} sx={{ alignSelf: "center" }} />}
          </ListItemButton>
        ))}
      </Box>

      <Typography
        variant="body2"
        color="primary"
        sx={{ mt: 2, cursor: "pointer", display: "inline-block" }}
        onClick={onManual}
      >
        Добавить без TMDB (вручную)
      </Typography>
    </Box>
  );
}

export const MovieList = () => (
  <List>
    <Datagrid rowClick="edit">
      <NumberField source="id" label="ID" />
      <TextField source="title" label="Название" />
      <SelectField source="genre" label="Жанр" choices={GENRE_CHOICES} />
      <SelectField source="status" label="Статус" choices={STATUS_CHOICES} />
      <NumberField source="duration" label="Мин" />
      <NumberField source="rating" label="Рейтинг" />
      <BooleanField source="is_featured" label="Главный" />
    </Datagrid>
  </List>
);

export const MovieCreate = () => {
  const [manual, setManual] = useState(false);

  if (manual) {
    return (
      <Create>
        <SimpleForm>
          <Typography
            variant="body2"
            color="primary"
            sx={{ cursor: "pointer", mb: 1 }}
            onClick={() => setManual(false)}
          >
            ← Поиск в TMDB
          </Typography>
          <MovieFormFields />
        </SimpleForm>
      </Create>
    );
  }

  return <TMDBSearch onManual={() => setManual(true)} />;
};

export const MovieEdit = () => (
  <Edit>
    <SimpleForm>
      <MovieFormFields />
    </SimpleForm>
  </Edit>
);
