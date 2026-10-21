from src.domain.enums import Role
from src.domain.errors import ValidationError, NotFound, PermissionDenied
from src.services.permissions import require_role


class CourseService:
    def __init__(self, course_repo, enrollment_repo):
        self.course_repo = course_repo
        self.enrollment_repo = enrollment_repo

    @require_role(Role.INSTRUCTOR)
    def create_course(self, acting_user, title, description, duration):
        title = title.strip()
        if not title:
            raise ValidationError("Course title is required.")

        description = description.strip() or None
        duration = duration.strip() or None

        return self.course_repo.create(acting_user.id, title, description, duration)
    
    @require_role(Role.INSTRUCTOR)
    def list_my_courses(self, acting_user):
        return self.course_repo.list_by_instructor(acting_user.id)
    
    @require_role(Role.INSTRUCTOR)
    def update_course(self, acting_user, course_id, title, description, duration):
        title = title.strip()

        if not title:
            raise ValidationError("Course title is required.")
        
        description = description.strip() or None
        duration = duration.strip() or None

        self._get_owned_course(acting_user, course_id)


        self.course_repo.update( course_id, title, description, duration)

    @require_role(Role.INSTRUCTOR)
    def delete_course(self, acting_user, course_id):
    
        self._get_owned_course(acting_user, course_id)

        self.course_repo.delete(course_id)

    @require_role(Role.INSTRUCTOR)
    def list_course_students(self, acting_user, course_id):
        self._get_owned_course(acting_user, course_id)
        return self.enrollment_repo.list_students_for_course(course_id)

    def _get_owned_course(self, acting_user, course_id):
        course = self.course_repo.get_by_id(course_id)
        if course is None:
            raise NotFound("Course is not found")
        if course["instructor_id"] !=  acting_user.id:
            raise PermissionDenied("You are not authorized to do this")
        return course
         
         
         
        



        
        

    
    



