# ADLY Frontend Architecture

## System Overview
```
┌─────────────────────────────────────────────────────────────────┐
│                     ADLY Frontend System                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │    React    │    │   Zustand   │    │ React Query │         │
│  │ Components  │◄──►│    Store    │◄──►│   Cache     │         │
│  │             │    │             │    │             │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                   │                   │              │
│         │                   │                   │              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ TailwindCSS │    │   Axios     │    │   i18next   │         │
│  │   Styling   │    │ HTTP Client │    │ Translation │         │
│  │             │    │             │    │             │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Application Structure
```
src/
├── components/           # Reusable UI components
│   ├── ui/              # Base UI components
│   ├── forms/           # Form components
│   └── charts/          # Analytics components
├── pages/               # Route-based pages
│   ├── auth/            # Authentication pages
│   ├── dashboard/       # Main dashboard
│   ├── campaigns/       # Campaign management
│   └── analytics/       # Analytics views
├── hooks/               # Custom React hooks
├── stores/              # Zustand state stores
├── services/            # API service layer
├── utils/               # Utility functions
└── types/               # TypeScript definitions
```

### 2. State Management (Zustand)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Auth Store    │    │ Campaign Store  │    │ Analytics Store │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • User data     │    │ • Active camps  │    │ • Metrics data  │
│ • Tokens        │    │ • Draft state   │    │ • Date ranges   │
│ • Permissions   │    │ • Form data     │    │ • Filters       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 3. Data Fetching (React Query)
- **Caching**: Automatic background refetching
- **Optimistic Updates**: Immediate UI feedback
- **Error Handling**: Retry logic and error boundaries
- **Real-time**: WebSocket integration for live updates

## Page Architecture

### Dashboard Layout
```
┌─────────────────────────────────────────────────────────────────┐
│                        Header Navigation                        │
├─────────────────┬───────────────────────────────────────────────┤
│                 │                                               │
│   Sidebar       │              Main Content Area               │
│   Navigation    │                                               │
│                 │  ┌─────────────────────────────────────────┐  │
│ • Dashboard     │  │                                         │  │
│ • Campaigns     │  │         Dynamic Page Content            │  │
│ • Analytics     │  │                                         │  │
│ • Settings      │  │                                         │  │
│                 │  └─────────────────────────────────────────┘  │
│                 │                                               │
└─────────────────┴───────────────────────────────────────────────┘
```

## Internationalization (Arabic-First)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Language      │    │   RTL Layout    │    │   Locale Data   │
│   Detection     │    │   Support       │    │   Formatting    │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Browser lang  │    │ • CSS direction │    │ • Date formats  │
│ • User pref     │    │ • Text align    │    │ • Number format │
│ • URL param     │    │ • Icon flip     │    │ • Currency      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Performance Optimization

### Code Splitting & Lazy Loading
```typescript
// Route-based code splitting
const Dashboard = lazy(() => import('../pages/Dashboard'));
const Campaigns = lazy(() => import('../pages/Campaigns'));
const Analytics = lazy(() => import('../pages/Analytics'));

// Component-based splitting for heavy components
const ChartComponent = lazy(() => import('../components/charts/AdvancedChart'));
const VideoEditor = lazy(() => import('../components/content/VideoEditor'));

// Preload critical routes
const preloadRoute = (routeComponent: () => Promise<any>) => {
  const componentImport = routeComponent();
  return componentImport;
};
```

### Bundle Optimization
```javascript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          charts: ['recharts', 'd3'],
          ui: ['@headlessui/react', 'framer-motion']
        }
      }
    }
  }
});
```

### Real-time Features
```typescript
// WebSocket integration for live updates
const useWebSocket = (url: string) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);

  useEffect(() => {
    const ws = new WebSocket(url);
    
    ws.onopen = () => {
      setIsConnected(true);
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLastMessage(data);
      
      // Update React Query cache with real-time data
      queryClient.setQueryData(['campaigns'], (oldData: any) => {
        if (data.type === 'campaign_update') {
          return updateCampaignInList(oldData, data.campaign);
        }
        return oldData;
      });
    };

    return () => ws.close();
  }, [url]);

  return { isConnected, lastMessage };
};
```

## Advanced State Management

### Zustand Store with Persistence
```typescript
interface CampaignStore {
  campaigns: Campaign[];
  activeCampaign: Campaign | null;
  draftCampaign: Partial<Campaign>;
  filters: CampaignFilters;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setCampaigns: (campaigns: Campaign[]) => void;
  setActiveCampaign: (campaign: Campaign) => void;
  updateDraftCampaign: (updates: Partial<Campaign>) => void;
  createCampaign: (campaignData: CreateCampaignData) => Promise<void>;
}

const useCampaignStore = create<CampaignStore>()(
  devtools(
    persist(
      (set, get) => ({
        campaigns: [],
        activeCampaign: null,
        draftCampaign: {},
        filters: {},
        isLoading: false,
        error: null,

        setCampaigns: (campaigns) => set({ campaigns }),
        
        setActiveCampaign: (campaign) => set({ activeCampaign: campaign }),
        
        updateDraftCampaign: (updates) => set((state) => ({
          draftCampaign: { ...state.draftCampaign, ...updates }
        })),

        createCampaign: async (campaignData) => {
          set({ isLoading: true, error: null });
          try {
            const response = await api.campaigns.create(campaignData);
            set((state) => ({
              campaigns: [...state.campaigns, response.data],
              isLoading: false,
              draftCampaign: {}
            }));
          } catch (error) {
            set({ error: error.message, isLoading: false });
          }
        }
      }),
      {
        name: 'campaign-store',
        partialize: (state) => ({ 
          draftCampaign: state.draftCampaign,
          filters: state.filters 
        })
      }
    )
  )
);
```

## Arabic-First RTL Support

### Direction-Aware Components
```typescript
const useDirection = () => {
  const { i18n } = useTranslation();
  return i18n.language === 'ar' ? 'rtl' : 'ltr';
};

const DirectionalComponent: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const direction = useDirection();
  
  return (
    <div 
      dir={direction} 
      className={`${direction === 'rtl' ? 'font-arabic' : 'font-latin'}`}
    >
      {children}
    </div>
  );
};

// RTL-aware animations
const slideInVariants = {
  hidden: (direction: string) => ({
    x: direction === 'rtl' ? 100 : -100,
    opacity: 0
  }),
  visible: {
    x: 0,
    opacity: 1,
    transition: { duration: 0.3 }
  }
};
```

### Arabic Typography & Styling
```css
/* Arabic font stack */
.font-arabic {
  font-family: 'Noto Sans Arabic', 'Cairo', 'Amiri', sans-serif;
  font-feature-settings: 'liga' 1, 'calt' 1;
}

/* RTL-specific utilities */
.rtl .ml-4 { margin-right: 1rem; margin-left: 0; }
.rtl .mr-4 { margin-left: 1rem; margin-right: 0; }
.rtl .pl-4 { padding-right: 1rem; padding-left: 0; }
.rtl .pr-4 { padding-left: 1rem; padding-right: 0; }

/* Arabic number formatting */
.arabic-numerals {
  font-variant-numeric: tabular-nums;
  direction: ltr;
  unicode-bidi: embed;
}
```

## Testing Strategy

### Component Testing with RTL Support
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { I18nextProvider } from 'react-i18next';
import i18n from '../i18n/config';

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });
  
  return render(
    <QueryClientProvider client={queryClient}>
      <I18nextProvider i18n={i18n}>
        {component}
      </I18nextProvider>
    </QueryClientProvider>
  );
};

// Test Arabic RTL functionality
describe('CampaignForm', () => {
  it('should render correctly in Arabic RTL mode', async () => {
    await i18n.changeLanguage('ar');
    
    renderWithProviders(<CampaignForm />);
    
    expect(document.dir).toBe('rtl');
    expect(screen.getByLabelText(/اسم الحملة/)).toBeInTheDocument();
  });
});
```

## Deployment Configuration

### Production Build
```dockerfile
# Multi-stage build for production
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```