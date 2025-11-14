"""
User Repository
Data access layer for User model CRUD operations.
Provides clean separation between database operations and business logic.
"""

from typing import Optional, List
from sqlalchemy.exc import IntegrityError
from extensions import db
from models.user import User


class UserRepository:
    """
    Repository for User model data access operations.
    Handles all database queries and operations for users.
    """
    
    @staticmethod
    def create(name: str, email: str, password: str, 
               role: str = 'student', department: Optional[str] = None) -> Optional[User]:
        """
        Create a new user in the database.
        
        Args:
            name: User's full name
            email: User's email (must be unique)
            password: Plain text password (will be hashed by model)
            role: User role ('student', 'staff', 'admin')
            department: User's department (optional)
        
        Returns:
            User: Created user object or None if email already exists
        
        Raises:
            IntegrityError: If email already exists
        """
        try:
            user = User(
                name=name,
                email=email,
                password=password,
                role=role,
                department=department
            )
            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            return None
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        """
        Retrieve a user by ID.
        
        Args:
            user_id: User's ID
        
        Returns:
            User: User object or None if not found
        """
        return User.query.get(user_id)
    
    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        """
        Retrieve a user by email address.
        
        Args:
            email: User's email address
        
        Returns:
            User: User object or None if not found
        """
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def get_all(status: Optional[str] = None, role: Optional[str] = None,
                limit: Optional[int] = None, offset: int = 0) -> List[User]:
        """
        Retrieve all users with optional filtering.
        
        Args:
            status: Filter by status ('active', 'pending', 'suspended')
            role: Filter by role ('student', 'staff', 'admin')
            limit: Maximum number of users to return
            offset: Number of users to skip (for pagination)
        
        Returns:
            List[User]: List of user objects
        """
        query = User.query
        
        if status:
            query = query.filter_by(status=status)
        
        if role:
            query = query.filter_by(role=role)
        
        query = query.order_by(User.created_at.desc())
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def update(user: User, **kwargs) -> User:
        """
        Update user attributes.
        
        Args:
            user: User object to update
            **kwargs: Field names and values to update
        
        Returns:
            User: Updated user object
        
        Note:
            Use set_password() method for password updates to ensure hashing
        """
        for key, value in kwargs.items():
            if hasattr(user, key) and key != 'password_hash':
                setattr(user, key, value)
        
        db.session.commit()
        return user
    
    @staticmethod
    def update_status(user: User, status: str) -> User:
        """
        Update user account status.
        
        Args:
            user: User object to update
            status: New status ('active', 'pending', 'suspended')
        
        Returns:
            User: Updated user object
        """
        user.status = status
        db.session.commit()
        return user
    
    @staticmethod
    def update_role(user: User, role: str) -> User:
        """
        Update user role.
        
        Args:
            user: User object to update
            role: New role ('student', 'staff', 'admin')
        
        Returns:
            User: Updated user object
        """
        user.role = role
        db.session.commit()
        return user
    
    @staticmethod
    def delete(user: User) -> bool:
        """
        Delete a user from the database.
        
        Args:
            user: User object to delete
        
        Returns:
            bool: True if successful
        
        Note:
            This is a hard delete. Consider soft delete (status='suspended')
            for production use to maintain referential integrity.
        """
        try:
            db.session.delete(user)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    @staticmethod
    def count(status: Optional[str] = None, role: Optional[str] = None) -> int:
        """
        Count users with optional filtering.
        
        Args:
            status: Filter by status ('active', 'pending', 'suspended')
            role: Filter by role ('student', 'staff', 'admin')
        
        Returns:
            int: Number of users matching criteria
        """
        query = User.query
        
        if status:
            query = query.filter_by(status=status)
        
        if role:
            query = query.filter_by(role=role)
        
        return query.count()
    
    @staticmethod
    def exists_by_email(email: str) -> bool:
        """
        Check if a user with the given email exists.
        
        Args:
            email: Email address to check
        
        Returns:
            bool: True if user exists, False otherwise
        """
        return User.query.filter_by(email=email).first() is not None
    
    @staticmethod
    def search_by_name(name_query: str, limit: int = 20) -> List[User]:
        """
        Search users by name (case-insensitive partial match).
        
        Args:
            name_query: Name search string
            limit: Maximum number of results
        
        Returns:
            List[User]: List of matching users
        """
        return User.query.filter(
            User.name.ilike(f'%{name_query}%')
        ).limit(limit).all()
