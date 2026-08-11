from typing import List, Optional
from sqlalchemy import create_engine, String, Boolean, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

#Base class for all models
class Base(DeclarativeBase):
    pass

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key = True)
    title: Mapped[str] = mapped_column(String(100), nullable = False)
    priority: Mapped [str] = mapped_column(String(20), default = "Medium")
    is_completed: Mapped[bool] = mapped_column(Boolean, default = False)

    def __repr__(self) -> str:
        status = "Done" if self.is_completed else "Pending"
        return f"<task [{self.id}]: {self.title} | Priority: {self.priority} | Status: {status} > "


# Format: postgresql://username:password@host:port/database_name
# Replace with your actual password
# This uses your system username (unaisa) for authentication
engine = create_engine("postgresql:///taskdb", echo=False)
Base.metadata.create_all(engine)

#----- CREATE ------
def create_task(session: Session, title: str, priority: str = "Medium") ->Task:
    new_task = Task(title = title, priority = priority)
    session.add(new_task)
    session.commit()
    session.refresh(new_task) #reload the instance to get the auto-generated id
    print(f"created: {new_task}")
    return new_task

#----- READ -----
def get_all_tasks(session: Session) ->List[Task]:
    stmt = select(Task)
    return list(session.scalars(stmt).all())

def get_pending_tasks(session:Session)-> List[Task]:
    stmt = select(Task).where(Task.is_completed == False)
    return list(session.scalars(stmt).all())


#----- UPDATE -----
def mark_task_complete(session: Session, task_id: int ) -> Optional[Task]|bool:
    task = session.get(Task, task_id) # Direct lookup by primary key
    if task:
        task.is_completed  = True
        session.commit()
        print(f"Updated Task #{task_id} marked done")
        return task
    print(f"Task #{task_id} not found.")
    return None

#----- DELETE -----
def delete_task(session: Session, task_id: int) -> bool:
    task = session.get(Task, task_id)
    if task:
        session.delete(task)
        session.commit()
        print (f" Task #{task_id} deleted.")
        return True

    print(f"Task #{task_id} not found.")
    return False

#-------------------- Execution Script ---------------------
if __name__ == "__main__":
    with Session(engine) as session:
        print("--- 1. Creating Task ---")
        create_task(session, "Learn SQLAlchemy" , priority = "High")
        create_task(session, "build project" , priority = "High")
        create_task(session, "read document" , priority = "low")

        print("\n--- 2. Fetching all tasks ---")
        all_tasks = get_all_tasks(session)
        for t in all_tasks:
            print(t)

        print("\n--- 3.Updating a task ---")
        mark_task_complete(session, task_id = 2)

        print("\n--- 4. Fetching Only Pending Tasks ---")
        pending = get_pending_tasks(session)
        for t in pending:
            print(t)

        print("\n--- 5.Deleteing a Task ---")
        delete_task(session, task_id = 3)

        print ("\n--- FINAL DATABASE STATE ---")
        for t in get_all_tasks(session):
            print(t)






