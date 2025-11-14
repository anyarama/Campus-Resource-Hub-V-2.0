import React, { useState, useEffect } from 'react';
import { 
  MoreVertical, 
  Download, 
  UserCheck, 
  UserX, 
  Plus,
  Rows3,
  Rows4
} from 'lucide-react';
import { toast } from 'sonner';
import { getUsers, updateUserStatus } from '../../api/services/adminService';
import type { User as ApiUser } from '../../api/types';
import { CHButton } from '../ui/ch-button';
import { CHBadge } from '../ui/ch-badge';
import { CHTable } from '../ui/ch-table';
import { CHDropdown } from '../ui/ch-dropdown';

/**
 * Admin Users Page
 * Enterprise table with bulk actions and density toggle
 */

interface User {
  id: number;
  name: string;
  email: string;
  role: 'Admin' | 'Staff' | 'Student';
  status: 'active' | 'pending' | 'suspended';
  created: string;
}

type Density = 'comfortable' | 'compact';

export function AdminUsers() {
  const [selectedRows, setSelectedRows] = useState<number[]>([]);
  const [density, setDensity] = useState<Density>('comfortable');
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  
  // Fetch users from backend
  useEffect(() => {
    async function fetchUsers() {
      setLoading(true);
      setError(null);
      
      const response = await getUsers();
      
      if (response.error) {
        const errorMessage = response.error || 'Failed to load users';
        setError(errorMessage);
        toast.error('Error loading users', {
          description: errorMessage,
        });
      } else if (response.data) {
        // Transform API users to match local interface
        const transformedUsers: User[] = response.data.items.map((user: ApiUser) => ({
          id: user.id,
          name: user.full_name || user.username,
          email: user.email,
          role: user.role === 'admin' ? 'Admin' : user.role === 'staff' ? 'Staff' : 'Student',
          status: user.status === 'inactive' ? 'pending' : user.status as 'active' | 'pending' | 'suspended',
          created: new Date(user.created_at).toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
          }),
        }));
        setUsers(transformedUsers);
      }
      
      setLoading(false);
    }
    
    fetchUsers();
  }, []);
  
  // Sample user data (fallback for when API is not available)
  const fallbackUsers: User[] = [
    {
      id: 1,
      name: 'Sarah Johnson',
      email: 'sjohnson@iu.edu',
      role: 'Admin',
      status: 'active',
      created: 'Jan 15, 2024',
    },
    {
      id: 2,
      name: 'Michael Chen',
      email: 'mchen@iu.edu',
      role: 'Staff',
      status: 'active',
      created: 'Feb 3, 2024',
    },
    {
      id: 3,
      name: 'Emily Rodriguez',
      email: 'erodriguez@iu.edu',
      role: 'Student',
      status: 'active',
      created: 'Mar 12, 2024',
    },
    {
      id: 4,
      name: 'David Park',
      email: 'dpark@iu.edu',
      role: 'Student',
      status: 'pending',
      created: 'Mar 20, 2024',
    },
    {
      id: 5,
      name: 'Jessica Williams',
      email: 'jwilliams@iu.edu',
      role: 'Staff',
      status: 'active',
      created: 'Apr 5, 2024',
    },
    {
      id: 6,
      name: 'Robert Taylor',
      email: 'rtaylor@iu.edu',
      role: 'Student',
      status: 'suspended',
      created: 'May 10, 2024',
    },
    {
      id: 7,
      name: 'Amanda Brown',
      email: 'abrown@iu.edu',
      role: 'Admin',
      status: 'active',
      created: 'Jun 8, 2024',
    },
    {
      id: 8,
      name: 'Christopher Lee',
      email: 'clee@iu.edu',
      role: 'Student',
      status: 'active',
      created: 'Jul 22, 2024',
    },
  ];
  
  // Get role badge variant
  const getRoleBadgeVariant = (role: User['role']) => {
    if (role === 'Admin') return 'crimson';
    if (role === 'Staff') return 'info';
    return 'neutral';
  };
  
  // Get status badge variant
  const getStatusBadgeVariant = (status: User['status']) => {
    if (status === 'active') return 'success';
    if (status === 'pending') return 'warning';
    return 'danger';
  };
  
  // Toggle row selection
  const toggleRowSelection = (id: number) => {
    if (selectedRows.includes(id)) {
      setSelectedRows(selectedRows.filter(rowId => rowId !== id));
    } else {
      setSelectedRows([...selectedRows, id]);
    }
  };
  
  // Toggle all rows
  const toggleAllRows = () => {
    if (selectedRows.length === users.length) {
      setSelectedRows([]);
    } else {
      setSelectedRows(users.map(u => u.id));
    }
  };
  
  // Bulk actions
  const handleActivate = async () => {
    if (selectedRows.length === 0) return;
    
    setActionLoading(-1); // -1 indicates bulk action
    
    try {
      const promises = selectedRows.map(id => updateUserStatus(id, 'active'));
      const results = await Promise.all(promises);
      
      const failures = results.filter(r => r.error);
      
      if (failures.length === 0) {
        toast.success(`Activated ${selectedRows.length} user(s) successfully`);
        // Update local state
        setUsers(users.map(user => 
          selectedRows.includes(user.id) 
            ? { ...user, status: 'active' }
            : user
        ));
        setSelectedRows([]);
      } else {
        toast.error('Some users could not be activated', {
          description: `${failures.length} of ${selectedRows.length} failed`,
        });
      }
    } catch (err) {
      toast.error('Failed to activate users');
    }
    
    setActionLoading(null);
  };
  
  const handleSuspend = async () => {
    if (selectedRows.length === 0) return;
    
    setActionLoading(-2); // -2 indicates bulk suspend
    
    try {
      const promises = selectedRows.map(id => updateUserStatus(id, 'suspended'));
      const results = await Promise.all(promises);
      
      const failures = results.filter(r => r.error);
      
      if (failures.length === 0) {
        toast.success(`Suspended ${selectedRows.length} user(s) successfully`);
        // Update local state
        setUsers(users.map(user => 
          selectedRows.includes(user.id) 
            ? { ...user, status: 'suspended' }
            : user
        ));
        setSelectedRows([]);
      } else {
        toast.error('Some users could not be suspended', {
          description: `${failures.length} of ${selectedRows.length} failed`,
        });
      }
    } catch (err) {
      toast.error('Failed to suspend users');
    }
    
    setActionLoading(null);
  };
  
  const handleExport = () => {
    console.log('Export users:', selectedRows);
  };
  
  // Row actions
  const handleRowAction = async (action: string, userId: number) => {
    if (action === 'suspend') {
      setActionLoading(userId);
      
      const response = await updateUserStatus(userId, 'suspended');
      
      if (response.error) {
        toast.error('Failed to suspend user', {
          description: response.error,
        });
      } else {
        toast.success('User suspended successfully');
        // Update local state
        setUsers(users.map(user => 
          user.id === userId ? { ...user, status: 'suspended' } : user
        ));
      }
      
      setActionLoading(null);
    } else {
      // Other actions not yet implemented
      toast.info(`${action} functionality coming soon`);
    }
  };
  
  // Cell padding based on density
  const cellPadding = density === 'comfortable' ? 'p-4' : 'p-2';
  
  return (
    <div className="min-h-screen bg-canvas">
      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-iu-crimson"></div>
        </div>
      )}
      
      {/* Error State */}
      {error && !loading && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 m-6">
          <p className="text-sm text-red-800">
            Failed to load users. Please try refreshing the page.
          </p>
        </div>
      )}
      
      {/* Main Content */}
      {!loading && !error && (
      <>
      {/* Admin Header - Normalized spacing */}
      <header className="bg-surface border-b border-default px-6 lg:px-8 py-8">
        <div className="max-w-[1400px] mx-auto">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div>
              <h1 className="text-h1 text-fg-default mb-2">User Management</h1>
              <p className="text-body text-fg-muted">
                View and manage all users, roles, and permissions
              </p>
            </div>
            
            {/* Header Actions */}
            <div className="flex items-center gap-2">
              {/* Density Toggle */}
              <div className="flex items-center gap-1 bg-subtle border border-default rounded-md p-1">
                <button
                  onClick={() => setDensity('comfortable')}
                  className={`
                    flex items-center gap-2 px-3 py-1.5 rounded
                    text-caption transition-colors
                    ${density === 'comfortable' 
                      ? 'bg-surface text-fg-default shadow-sm' 
                      : 'text-fg-muted hover:text-fg-default'
                    }
                  `}
                  title="Comfortable density"
                >
                  <Rows3 className="w-4 h-4" />
                  Comfortable
                </button>
                <button
                  onClick={() => setDensity('compact')}
                  className={`
                    flex items-center gap-2 px-3 py-1.5 rounded
                    text-caption transition-colors
                    ${density === 'compact' 
                      ? 'bg-surface text-fg-default shadow-sm' 
                      : 'text-fg-muted hover:text-fg-default'
                    }
                  `}
                  title="Compact density"
                >
                  <Rows4 className="w-4 h-4" />
                  Compact
                </button>
              </div>
              
              <CHButton variant="primary">
                <Plus className="w-4 h-4" />
                Add User
              </CHButton>
            </div>
          </div>
        </div>
      </header>
      
      {/* Bulk Actions Bar */}
      {selectedRows.length > 0 && (
        <div className="
          flex items-center justify-between gap-4 
          px-4 py-3 
          bg-[#FFF5F5] border border-[#FFE0E0] rounded-lg
          animate-slide-up
        ">
          <p className="text-caption-semibold text-fg-default">
            {selectedRows.length} user{selectedRows.length > 1 ? 's' : ''} selected
          </p>
          
          <div className="flex items-center gap-2">
              <CHButton
                variant="secondary"
                size="sm"
                onClick={handleActivate}
                disabled={actionLoading === -1}
              >
                {actionLoading === -1 ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
                ) : (
                  <UserCheck className="w-4 h-4" />
                )}
                Activate
              </CHButton>
              
              <CHButton
                variant="secondary"
                size="sm"
                onClick={handleSuspend}
                disabled={actionLoading === -2}
              >
                {actionLoading === -2 ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
                ) : (
                  <UserX className="w-4 h-4" />
                )}
                Suspend
              </CHButton>
            
            <CHButton
              variant="secondary"
              size="sm"
              onClick={handleExport}
            >
              <Download className="w-4 h-4" />
              Export
            </CHButton>
          </div>
        </div>
      )}
      
      {/* Table */}
      <CHTable
        columns={[
          {
            key: 'name',
            header: 'Name',
            sortable: true,
            render: (user: User) => (
              <span className="text-caption-semibold text-fg-default">
                {user.name}
              </span>
            ),
          },
          {
            key: 'email',
            header: 'Email',
            sortable: true,
            render: (user: User) => (
              <span className="text-caption text-fg-muted">
                {user.email}
              </span>
            ),
          },
          {
            key: 'role',
            header: 'Role',
            sortable: true,
            render: (user: User) => (
              <CHBadge variant={getRoleBadgeVariant(user.role)}>
                {user.role}
              </CHBadge>
            ),
            width: '120px',
          },
          {
            key: 'status',
            header: 'Status',
            sortable: true,
            render: (user: User) => (
              <CHBadge variant={getStatusBadgeVariant(user.status)}>
                {user.status.charAt(0).toUpperCase() + user.status.slice(1)}
              </CHBadge>
            ),
            width: '120px',
          },
          {
            key: 'created',
            header: 'Created',
            sortable: true,
            render: (user: User) => (
              <span className="text-caption text-fg-muted">
                {user.created}
              </span>
            ),
            width: '120px',
          },
          {
            key: 'actions',
            header: '',
            render: (user: User) => (
              <CHDropdown
                trigger={
                  <button 
                    className="p-1 hover:bg-subtle rounded transition-colors"
                    disabled={actionLoading === user.id}
                  >
                    {actionLoading === user.id ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
                    ) : (
                      <MoreVertical className="w-4 h-4 text-fg-muted" />
                    )}
                  </button>
                }
                items={[
                  { label: 'Edit User', onClick: () => handleRowAction('edit', user.id) },
                  { label: 'View Details', onClick: () => handleRowAction('view', user.id) },
                  { label: 'Reset Password', onClick: () => handleRowAction('reset', user.id) },
                  { type: 'separator' },
                  { label: 'Suspend User', onClick: () => handleRowAction('suspend', user.id), danger: true },
                  { label: 'Delete User', onClick: () => handleRowAction('delete', user.id), danger: true },
                ]}
              />
            ),
            width: '64px',
          },
        ]}
        data={users}
        density={density}
        selectable
        selectedRows={new Set(selectedRows.map(String))}
        onSelectionChange={(newSelection) => {
          setSelectedRows(Array.from(newSelection).map(Number));
        }}
        getRowId={(user: User) => String(user.id)}
      />
      </>
      )}
    </div>
  );
}
